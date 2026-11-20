"""Demo runner: Scene A (reuse) + Scene B (Guardian block).

Usage:
    python -m src.demo              # mock mode (default, no key)
    python -m src.demo --mode live  # live Meko datapack (needs .env)

The demo labels its mode on every line of output, so mock output is never
presented as live Meko output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.agents import guardian, observer, storyteller
from src.config import load_config
from src.llm import build_llm
from src.meko_client import build_client
from src.trace import write_trace

ROOT = Path(__file__).resolve().parent.parent


def load_sample_data() -> tuple[list[dict], list[dict]]:
    memories = json.loads((ROOT / "data" / "sample_memories.json").read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in (ROOT / "data" / "sample_events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return memories["shared_memories"], events


def run(mode: str) -> dict:
    import os

    os.environ["MEKO_MODE"] = mode
    cfg = load_config()
    client = build_client(cfg)
    llm = build_llm(cfg)
    print(f"[mode={cfg.mode}] datapack={cfg.meko_datapack_id} client={type(client).__name__}")
    print(f"[mode={cfg.mode}] datapacks: {client.datapack_list()}")

    shared, events = load_sample_data()
    # Seed the mock datapack with the shared sample memories.
    if cfg.mode == "mock":
        for mem in shared:
            added = client.memory_add(mem["text"], "observer", {"sample_id": mem["id"]})
            client.memory_promote([added["memory_id"]], "observer")

    print("\n--- Scene A: Agent A learns, Agent B reuses ---")
    thunder = next(e for e in events if e["event_id"] == "E-02")
    observer.log_event(client, thunder)
    print(f"Observer logged: {thunder['text']}")
    story = storyteller.draft_story(client, llm, "thunder rainy day story")
    print(f"Storyteller draft ({story['match_quality']}): {story['draft']}")
    print("Memories used:", [m.get("text", "")[:60] for m in story["memories"]])
    verdict_a = guardian.review(client, story["draft"], story["memories"])
    print(f"Guardian verdict on Scene A draft: {verdict_a.verdict.upper()}")

    print("\n--- Scene B: the Guardian blocks human speech ---")
    bad_draft = storyteller.draft_violating_story()
    print(f"Draft under review: {bad_draft}")
    trace = guardian.review(client, bad_draft, story["memories"])
    json_path, md_path = write_trace(trace, ROOT / "traces")
    print(f"Guardian verdict: {trace.verdict.upper()} (rule {trace.rule_id})")
    print(f"Explanation: {trace.explanation}")
    print(f"Trace written: {json_path} and {md_path}")
    try:
        client.artifact_put(md_path.name, md_path.read_text(encoding="utf-8"))
        print("Trace stored as datapack artifact.")
    except Exception as exc:  # live server may not expose artifact_put
        print(f"Artifact store unavailable ({exc}); trace kept as local file + conversation turn.")
    conv = client.conversation_create("guardian", title=f"Guardian trace {trace.trace_id}")
    client.conversation_add_message(
        conv.get("conversation_id", "mock-conv"),
        "guardian",
        input_text=f"Draft reviewed: {bad_draft}",
        output_text=f"Verdict {trace.verdict.upper()} under {trace.rule_id}. {trace.explanation}",
    )

    result = {
        "mode": cfg.mode,
        "scene_a_verdict": verdict_a.verdict,
        "scene_b_verdict": trace.verdict,
        "scene_b_rule": trace.rule_id,
        "trace_id": trace.trace_id,
    }
    assert result["scene_b_verdict"] == "block", "Scene B must end in a block"
    print(f"\nDemo complete: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    args = parser.parse_args()
    run(args.mode)


if __name__ == "__main__":
    main()
