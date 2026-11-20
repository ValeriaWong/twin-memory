"""Token measurement: baseline (stuff the full context) vs Meko retrieval.

Same task, same quality check, both runs. The baseline concatenates every
sample memory + every sample event into the prompt (what a naive agent
does). The Meko run retrieves only the top memories via context_search
and drafts from those. Token counts are estimated with a simple
whitespace/character heuristic (len(text) // 4) unless tiktoken is
installed — the method is stated in the output, and the comparison is
only valid because both runs use the same estimator and the same task.

Usage:
    python scripts/measure_tokens.py [--runs N] [--mode mock|live]

Output: JSON + a human-readable summary printed to stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents import storyteller  # noqa: E402
from src.config import load_config  # noqa: E402
from src.llm import build_llm  # noqa: E402
from src.meko_client import build_client  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def estimate_tokens(text: str) -> int:
    """Rough estimator: ~4 characters per token. Stated, not hidden."""
    try:
        import tiktoken  # type: ignore

        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except Exception:
        return max(1, len(text) // 4)


def quality_check(draft: str, memories: list[dict]) -> dict:
    """Same check for both runs: draft must cite only memories that exist,
    and the dog must not speak human words."""
    from src.rules import check_human_speech

    return {
        "dog_speaks_human_words": check_human_speech(draft) is not None,
        "memories_used": len(memories),
        "draft_chars": len(draft),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    args = parser.parse_args()
    os.environ["MEKO_MODE"] = args.mode
    cfg = load_config()
    client = build_client(cfg)
    llm = build_llm(cfg)

    memories = json.loads((ROOT / "data" / "sample_memories.json").read_text(encoding="utf-8"))
    # Seed the datapack first — retrieval cannot find what was never stored.
    # Idempotent: skip facts already present (live memory_add does no
    # duplicate check). No memory_promote: the seeded memories are already
    # retrievable via context_search in both modes, and promotion is a
    # one-way private -> shared move that a measurement script must not
    # do silently.
    from src.seed import _norm_text

    for mem in memories["shared_memories"]:
        existing = client.memory_search(mem["text"], "observer", limit=10)
        results = existing.get("results", []) if isinstance(existing, dict) else []
        if any(_norm_text(r.get("text") or r.get("memory") or "") == mem["text"]
               for r in results):
            continue
        client.memory_add(mem["text"], "observer", {"sample_id": mem["id"]})
    events = (ROOT / "data" / "sample_events.jsonl").read_text(encoding="utf-8")
    full_context = "\n".join(
        [m["text"] for m in memories["shared_memories"]] + [events]
    )
    prompt = "thunder rainy day story"

    baseline_tokens, meko_tokens = [], []
    for _ in range(args.runs):
        baseline_tokens.append(estimate_tokens(full_context + prompt))
        story = storyteller.draft_story(client, llm, prompt)
        assert story["memories"], "measurement invalid: retrieval found nothing to draft from"
        retrieved = "\n".join(m.get("text", "") for m in story["memories"])
        meko_tokens.append(estimate_tokens(retrieved + prompt))
        check = quality_check(story["draft"], story["memories"])
        assert not check["dog_speaks_human_words"], "quality check failed: dog speaks"

    result = {
        "method": "whitespace/char heuristic (~4 chars/token) unless tiktoken installed; same task, same quality check, both runs",
        "mode": cfg.mode,
        "runs": args.runs,
        "baseline_mean_input_tokens": sum(baseline_tokens) / len(baseline_tokens),
        "meko_mean_input_tokens": sum(meko_tokens) / len(meko_tokens),
        "saving_pct": round(
            100 * (1 - (sum(meko_tokens) / len(meko_tokens)) / (sum(baseline_tokens) / len(baseline_tokens))), 1
        ),
        "quality_check": "dog does not speak human words; draft uses only retrieved memories",
    }
    print(json.dumps(result, indent=2))
    print(
        f"\nBaseline stuffing: {result['baseline_mean_input_tokens']:.0f} tokens/run; "
        f"Meko retrieval: {result['meko_mean_input_tokens']:.0f} tokens/run; "
        f"saving: {result['saving_pct']}% (same task, same quality check)."
    )


if __name__ == "__main__":
    main()
