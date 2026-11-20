"""Seed the datapack from data/sample_memories.json (synthetic text only).

Mock mode: loads into the in-memory mock datapack.
Live mode: checks memory_search first and skips facts already present
(Meko does no duplicate check on memory_add, so the seed script must).

Usage:
    python -m src.seed              # mock
    python -m src.seed --mode live  # live datapack (needs .env)
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from src.config import load_config
from src.meko_client import build_client

ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_DOCS = {
    "identity-summary.md": (
        "# Identity summary (twinpet_001, frozen 2026-11-04)\n\n"
        "Cream-white coat, irregular light-tan markings; lean, lightweight; "
        "asymmetric semi-folded ears; mostly-white curled tail; white muzzle, "
        "black nose.\n\n"
        "Eyes — two versions, both recorded, neither silently resolved: "
        "digital appearance (owner-chosen, both eyes healthy dark-brown) vs "
        "biological fact (real dog's right eye area fully white, no "
        "dark-brown stripe). The Guardian does not use eye colour as an "
        "identity check.\n\n"
        "Limits: 4 frames only, 480x360, no pure front view, t10 lower half "
        "blocked by a sheet.\n"
    ),
    "rule-book.md": (
        "# Rule book\n\n"
        "R-01 The twin never speaks human speech. Dog sounds and behaviour only.\n"
        "R-02 Every claimed event in a story must already be in shared memory, with a source.\n"
        "R-03 Behaviour must stay inside the recorded temper and boundaries.\n"
        "R-04 No frozen identity fact may be contradicted.\n"
        "R-05 Inferred facts are labelled inferred, never presented as observed.\n"
        "Promotion private -> shared is one-way and needs explicit confirmation.\n"
    ),
    "story-bible.md": (
        "# Story bible\n\n"
        "World: the dog, the owner, the home, the small park two streets away.\n"
        "Sampling set for next beats (not fixed branches): greet / explore / "
        "rest / play / hide-from-thunder / seek-owner.\n"
        "hide-from-thunder requires the thunder-fear memory (S-02).\n"
    ),
}


def _norm_text(t: str) -> str:
    """Repair Meko's latin-1 mojibake for duplicate comparison.

    The live server stores non-ASCII (e.g. the em-dash in P-01) as the
    UTF-8 bytes re-read as latin-1, so an exact-text check against the
    source file never matches. Re-encoding repairs it; pure ASCII is
    unaffected.
    """
    try:
        return t.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return t


def upload_knowledge(client, docs: dict[str, str]) -> None:
    """Upload knowledge docs to the live datapack.

    knowledgebase_upload_document returns a presigned URL (valid 5 min,
    exact size + SHA-256 enforced); the agent then PUTs the file bytes
    to that URL and polls knowledgebase_document_status until indexing
    completes. Mock mode has no server, so this is live-only.
    """
    import base64
    import hashlib
    import time

    import requests

    for name, text in docs.items():
        raw = text.encode("utf-8")
        resp = client._tool("knowledgebase_upload_document", {
            "filename": name,
            "size": len(raw),
            "content_hash": hashlib.sha256(raw).hexdigest(),
            "content_head_base64": base64.b64encode(raw[:3072]).decode("ascii"),
        })
        if resp.get("already_uploaded"):
            print(f"  - {name}: already uploaded, skipping")
            continue
        url = resp.get("upload_url") or resp.get("url")
        key = resp.get("key") or resp.get("document_key")
        if not url:
            raise RuntimeError(f"knowledge upload for {name} returned no URL: {resp!r}")
        put = requests.put(url, data=raw, timeout=60,
                           headers={"Content-Type": "text/markdown"})
        put.raise_for_status()
        for _ in range(12):
            status = client._tool("knowledgebase_document_status",
                                  {"document_key": key})
            state = status.get("state") if isinstance(status, dict) else None
            if state == "completed":
                print(f"  - {name}: indexed (completed)")
                break
            if state in ("failed", "abandoned", "oversized"):
                raise RuntimeError(f"knowledge upload for {name} ended {state}: {status!r}")
            time.sleep(5)
        else:
            print(f"  - {name}: upload sent, indexing still {state!r} after ~60s")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    parser.add_argument("--upload-kb", action="store_true",
                        help="also upload the three knowledge docs (live only)")
    args = parser.parse_args()
    os.environ["MEKO_MODE"] = args.mode
    cfg = load_config()
    client = build_client(cfg)
    print(f"[mode={cfg.mode}] datapack={cfg.meko_datapack_id}")

    data = json.loads((ROOT / "data" / "sample_memories.json").read_text(encoding="utf-8"))
    for mem in data["shared_memories"]:
        # Exact-text duplicate check only: Meko does no duplicate check on
        # memory_add, and a fuzzy query would false-positive on shared words
        # like "dog". Skip only if the exact text is already stored.
        existing = client.memory_search(mem["text"], "observer", limit=10)
        results = existing.get("results", []) if isinstance(existing, dict) else []
        # Live search results carry the text under "memory"; the mock
        # uses "text". Check both, or a re-run would double-add.
        if any(_norm_text(r.get("text") or r.get("memory") or "") == mem["text"] for r in results):
            print(f"skip (already present): {mem['id']}")
            continue
        added = client.memory_add(mem["text"], "observer", {"sample_id": mem["id"]})
        mid = (added.get("memory_id") or added.get("id")) if isinstance(added, dict) else added
        print(f"seeded shared memory {mem['id']}: {mid}")
    for mem in data["private_memories"]:
        existing = client.memory_search(mem["text"], "observer", limit=10)
        results = existing.get("results", []) if isinstance(existing, dict) else []
        if any(_norm_text(r.get("text") or r.get("memory") or "") == mem["text"] for r in results):
            print(f"skip (already present): {mem['id']}")
            continue
        added = client.memory_add(mem["text"], "observer", {"sample_id": mem["id"]})
        mid = (added.get("memory_id") or added.get("id")) if isinstance(added, dict) else added
        print(f"seeded PRIVATE memory {mem['id']} (not promoted): {mid}")

    print("Knowledge documents to upload via the Meko portal / knowledgebase_upload_document:")
    for name in KNOWLEDGE_DOCS:
        print(f"  - {name} ({len(KNOWLEDGE_DOCS[name])} bytes)")
    if args.upload_kb:
        if cfg.mode != "live":
            raise SystemExit("--upload-kb needs --mode live")
        print("Uploading knowledge documents to the live datapack:")
        upload_knowledge(client, KNOWLEDGE_DOCS)
    print("Done. In live mode, upload the three documents and check indexing completes.")


if __name__ == "__main__":
    main()
