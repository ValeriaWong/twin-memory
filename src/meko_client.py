"""Meko client: live MCP over HTTPS, plus an offline in-memory mock.

Live path (verified against Meko docs, 2026-11-20):
- One endpoint for every client: https://mcp.mekodata.ai/mcp
- Auth: Authorization: Bearer <key> AND a User-Agent header. Meko rejects
  requests without either. Keys start with ``mko_tkn_`` and are shown once.
- Protocol: MCP (JSON-RPC 2.0) — ``initialize`` then ``tools/call``.
  The datapack is selected per call via ``datapack_id``.
- Tool names used here are the exact names from
  docs.mekodata.ai/reference/mcp-server/: context_search,
  conversation_create, conversation_add_message, memory_add, memory_search,
  memory_promote, knowledgebase_search, track_token_usage, datapack_list,
  selflearning_status.

Mock path: same interface, in-memory store, zero network, zero keys. The
demo labels its mode on screen, so mock output is never presented as live.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

import requests


class MekoError(RuntimeError):
    pass


class BaseMekoClient:
    """Shared interface. Both live and mock implement these methods."""

    def datapack_list(self) -> list[dict]:
        raise NotImplementedError

    def context_search(self, query: str, agent_id: str, limit: int = 10) -> dict:
        raise NotImplementedError

    def memory_search(self, query: str, agent_id: str, limit: int = 10) -> dict:
        raise NotImplementedError

    def memory_add(self, text: str, agent_id: str, metadata: dict | None = None) -> dict:
        raise NotImplementedError

    def memory_promote(self, memory_ids: list[str], agent_id: str) -> dict:
        raise NotImplementedError

    def conversation_create(self, agent_id: str, title: str) -> dict:
        raise NotImplementedError

    def conversation_add_message(
        self, conversation_id: str, agent_id: str, input_text: str, output_text: str
    ) -> dict:
        raise NotImplementedError

    def track_token_usage(
        self, conversation_id: str, name: str, input_tokens: int, output_tokens: int, model: str
    ) -> dict:
        raise NotImplementedError

    def artifact_put(self, name: str, content: str) -> dict:
        """Store a whole file. Optional: see datapack-schema.md note.

        The live MCP reference groups artifact tools as ``artifact_*``
        without spelling out every name in the verified excerpt. This method
        tries the documented tool and, if the server does not expose it,
        raises MekoError with a clear message — callers must fall back to
        storing the trace as a conversation turn + local file, and say so.
        """
        raise NotImplementedError


class MekoClient(BaseMekoClient):
    """Live client: MCP JSON-RPC over Streamable HTTP."""

    def __init__(self, mcp_url: str, api_key: str, datapack_id: str) -> None:
        if not api_key.startswith("mko_tkn_"):
            raise MekoError(
                "MEKO_API_KEY does not start with 'mko_tkn_'. Generate one in "
                "Meko Settings > API Keys; do not use any other token."
            )
        self.mcp_url = mcp_url.rstrip("/")
        self.datapack_id = datapack_id
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "twin-memory-contextcon/1.0",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            }
        )
        self._request_id = 0
        self._session_id: str | None = None
        self._conversation_id: str | None = None
        self._initialize()

    def _rpc(self, method: str, params: dict) -> Any:
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params,
        }
        headers = dict(self.session.headers)
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        resp = self.session.post(self.mcp_url, json=payload, headers=headers, timeout=60)
        # Streamable HTTP returns SSE ("event: message\ndata: {...}\n\n"),
        # not a bare JSON body. Extract the data payload before parsing.
        text = resp.text.strip()
        if not text.startswith("{"):
            data_lines = [
                line[5:].strip()
                for line in text.splitlines()
                if line.startswith("data:")
            ]
            text = data_lines[-1] if data_lines else ""
        resp.raise_for_status()
        data = json.loads(text) if text else {}
        if "error" in data:
            raise MekoError(f"MCP {method} failed: {data['error']}")
        return data.get("result", data)

    def _initialize(self) -> None:
        self._rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "twin-memory", "version": "1.0"},
            },
        )

    def list_tools(self) -> list[dict]:
        """List the server's tools — verify names live before trusting them."""
        result = self._rpc("tools/list", {})
        return result.get("tools", []) if isinstance(result, dict) else []

    def _tool(self, name: str, arguments: dict) -> Any:
        # Live server wraps every tools/call result in FastMCP content
        # blocks (see _unwrap) and requires a conversation_id on every
        # call except conversation_create itself.
        args = dict(arguments)
        args["datapack_id"] = self.datapack_id
        if name != "conversation_create":
            args["conversation_id"] = self._ensure_conversation()
        result = self._rpc(
            "tools/call", {"name": name, "arguments": args}
        )
        unwrapped = self._unwrap(result)
        if isinstance(result, dict) and result.get("isError"):
            raise MekoError(f"Meko tool {name!r} failed: {unwrapped}")
        return unwrapped

    def _ensure_conversation(self) -> str:
        if self._conversation_id is None:
            created = self._tool(
                "conversation_create",
                {"agent_id": "twin-memory", "title": "ContextCon live run"},
            )
            cid = (created or {}).get("conversation_id") or (created or {}).get("id")
            if not cid:
                raise MekoError(
                    f"conversation_create returned no id: {created!r}")
            self._conversation_id = cid
        return self._conversation_id

    @staticmethod
    def _unwrap(result: Any) -> Any:
        """Unwrap a FastMCP tools/call result.

        The server returns {"content": [{"type": "text", "text":
        "<json string>"}], "structuredContent": {"result": "<json
        string>"}} — parse the JSON string, preferring
        structuredContent.result. Plain values pass through.
        """
        if isinstance(result, dict) and "content" in result:
            sc = result.get("structuredContent") or {}
            text = sc.get("result")
            if text is None:
                content = result.get("content") or []
                text = content[0].get("text") if content else None
            if isinstance(text, str):
                try:
                    return json.loads(text)
                except ValueError:
                    return text
            return text
        return result

    def datapack_list(self) -> list[dict]:
        result = self._tool("datapack_list", {})
        return result if isinstance(result, list) else result.get("datapacks", [])

    def context_search(self, query: str, agent_id: str, limit: int = 10) -> dict:
        return self._tool(
            "context_search",
            {"query": query, "agent_id": agent_id, "limit": limit},
        )

    def memory_search(self, query: str, agent_id: str, limit: int = 10) -> dict:
        return self._tool(
            "memory_search", {"query": query, "agent_id": agent_id, "limit": limit}
        )

    def memory_add(self, text: str, agent_id: str, metadata: dict | None = None) -> dict:
        # The live server validates metadata as a string, not an object —
        # a dict is rejected with a pydantic string_type error and
        # nothing is stored. Send it JSON-encoded.
        return self._tool(
            "memory_add",
            {"text": text, "agent_id": agent_id,
             "metadata": json.dumps(metadata or {})},
        )

    def memory_promote(self, memory_ids: list[str], agent_id: str) -> dict:
        # One-way, owner/maintainer only, needs explicit confirmation.
        # Callers must confirm with the user before invoking this.
        return self._tool(
            "memory_promote", {"memory_ids": memory_ids, "agent_id": agent_id}
        )

    def conversation_create(self, agent_id: str, title: str) -> dict:
        return self._tool(
            "conversation_create",
            {"agent_id": agent_id, "title": title, "session_id": str(uuid.uuid4())},
        )

    def conversation_add_message(
        self, conversation_id: str, agent_id: str, input_text: str, output_text: str
    ) -> dict:
        return self._tool(
            "conversation_add_message",
            {
                "conversation_id": conversation_id,
                "agent_id": agent_id,
                "input": input_text,
                "output": output_text,
            },
        )

    def track_token_usage(
        self, conversation_id: str, name: str, input_tokens: int, output_tokens: int, model: str
    ) -> dict:
        return self._tool(
            "track_token_usage",
            {
                "conversation_id": conversation_id,
                "name": name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "model": model,
            },
        )

    def artifact_put(self, name: str, content: str) -> dict:
        # Documented inputs (reference, verified 2026-11-21): filename,
        # content_base64, content_type, conversation_id, datapack_id.
        import base64

        try:
            return self._tool(
                "artifact_put",
                {
                    "filename": name,
                    "content_base64": base64.b64encode(
                        content.encode("utf-8")).decode("ascii"),
                    "content_type": "text/markdown",
                },
            )
        except Exception as exc:  # server may not expose this name; be honest
            raise MekoError(
                f"artifact_put not available on this server ({exc}). Store the "
                "trace as a conversation turn + local file instead, and say so."
            ) from exc


class MockMekoClient(BaseMekoClient):
    """Offline in-memory datapack. Same interface, no network, no key."""

    def __init__(self, datapack_id: str = "twin-memory") -> None:
        self.datapack_id = datapack_id
        self.shared: list[dict] = []
        self.private: list[dict] = []
        self.conversations: dict[str, list[dict]] = {}
        self.artifacts: dict[str, str] = {}
        self.token_log: list[dict] = []
        self._counter = 0

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix}-{self._counter:03d}"

    def datapack_list(self) -> list[dict]:
        return [{"datapack_id": self.datapack_id, "name": self.datapack_id}]

    def _search(self, items: list[dict], query: str, limit: int) -> list[dict]:
        import re

        def tokens(text: str) -> list[str]:
            return re.findall(r"[a-z0-9]+", text.lower())

        def matches(q: str, t: str) -> bool:
            # Exact, substring, or shared 4-letter stem ("rainy" ~ "rain").
            return q in t or t in q or (len(q) >= 4 and len(t) >= 4 and q[:4] == t[:4])

        scored = []
        for item in items:
            text_tokens = tokens(item.get("text", ""))
            hits = sum(1 for w in tokens(query) if len(w) > 2 and any(matches(w, t) for t in text_tokens))
            if hits:
                scored.append({**item, "score": round(hits / max(len(tokens(query)), 1), 2)})
        scored.sort(key=lambda x: -x["score"])
        return scored[:limit]

    def context_search(self, query: str, agent_id: str, limit: int = 10) -> dict:
        mem = self._search(self.shared, query, limit)
        return {
            "memory": mem,
            "knowledge_base": [],
            "conversation": [],
            "match_quality": "strong" if mem else "weak",
            "agent_hint": "Top shared memory found." if mem else "No matching memory; add the missing fact once.",
        }

    def memory_search(self, query: str, agent_id: str, limit: int = 10) -> dict:
        return {"results": self._search(self.shared + self.private, query, limit)}

    def memory_add(self, text: str, agent_id: str, metadata: dict | None = None) -> dict:
        mem = {
            "memory_id": self._next_id("mem"),
            "text": text,
            "agent_id": agent_id,
            "metadata": metadata or {},
        }
        self.private.append(mem)
        return mem

    def memory_promote(self, memory_ids: list[str], agent_id: str) -> dict:
        moved = []
        for mem in list(self.private):
            if mem["memory_id"] in memory_ids:
                self.private.remove(mem)
                self.shared.append(mem)
                moved.append(mem["memory_id"])
        return {"promoted": moved, "note": "One-way: removed from private store."}

    def conversation_create(self, agent_id: str, title: str) -> dict:
        conv_id = self._next_id("conv")
        self.conversations[conv_id] = []
        return {"conversation_id": conv_id, "title": title}

    def conversation_add_message(
        self, conversation_id: str, agent_id: str, input_text: str, output_text: str
    ) -> dict:
        self.conversations.setdefault(conversation_id, []).append(
            {"agent_id": agent_id, "input": input_text, "output": output_text}
        )
        return {"conversation_id": conversation_id, "messages": len(self.conversations[conversation_id])}

    def track_token_usage(
        self, conversation_id: str, name: str, input_tokens: int, output_tokens: int, model: str
    ) -> dict:
        entry = {
            "conversation_id": conversation_id,
            "name": name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "model": model,
        }
        self.token_log.append(entry)
        return entry

    def artifact_put(self, name: str, content: str) -> dict:
        self.artifacts[name] = content
        return {"name": name, "bytes": len(content.encode("utf-8"))}


def build_client(cfg) -> BaseMekoClient:
    if cfg.live:
        return MekoClient(cfg.meko_mcp_url, cfg.meko_api_key, cfg.meko_datapack_id)
    return MockMekoClient(cfg.meko_datapack_id)
