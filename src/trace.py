"""Decision-trace logger. Every Guardian verdict leaves a trace that a
non-technical person can read in under two minutes — and that can be replayed.

A trace records: verdict, rule fired, memories consulted (with Meko memory
ids and relevance scores), facts that were missing, and a plain-language
explanation. It is written as JSON (machine-readable) and Markdown
(human-readable), stored as a Meko artifact when available, and also as a
conversation turn so it is searchable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Trace:
    trace_id: str
    verdict: str  # allow | change | block
    rule_id: str
    rule_text: str
    memories_consulted: list[dict] = field(default_factory=list)
    missing_facts: list[str] = field(default_factory=list)
    explanation: str = ""
    draft: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "verdict": self.verdict,
            "rule_id": self.rule_id,
            "rule_text": self.rule_text,
            "memories_consulted": self.memories_consulted,
            "missing_facts": self.missing_facts,
            "explanation": self.explanation,
            "draft": self.draft,
            "created_at": self.created_at or datetime.now(timezone.utc).isoformat(),
        }

    def to_markdown(self) -> str:
        lines = [
            f"# Decision trace {self.trace_id}",
            "",
            f"**Verdict:** {self.verdict.upper()}",
            f"**Rule:** {self.rule_id} — {self.rule_text}",
            "",
            "## Draft checked",
            "",
            f"> {self.draft}",
            "",
            "## Memories consulted",
            "",
        ]
        if self.memories_consulted:
            for mem in self.memories_consulted:
                lines.append(
                    f"- {mem.get('memory_id', '?')} (score {mem.get('score', '?')}): "
                    f"{mem.get('text', '')}"
                )
        else:
            lines.append("- None.")
        lines += ["", "## Missing facts", ""]
        lines += [f"- {m}" for m in self.missing_facts] or ["- None needed for this verdict."]
        lines += ["", "## Why", "", self.explanation, ""]
        return "\n".join(lines)


def write_trace(trace: Trace, traces_dir: Path | str = "traces") -> tuple[Path, Path]:
    """Write JSON + Markdown to traces/. Returns both paths."""
    traces_dir = Path(traces_dir)
    traces_dir.mkdir(parents=True, exist_ok=True)
    json_path = traces_dir / f"{trace.trace_id}.json"
    md_path = traces_dir / f"{trace.trace_id}.md"
    json_path.write_text(json.dumps(trace.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(trace.to_markdown(), encoding="utf-8")
    return json_path, md_path
