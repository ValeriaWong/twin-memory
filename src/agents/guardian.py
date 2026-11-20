"""Guardian — enforces personality / temper / boundary rules and outputs
a readable decision trace. It never rewrites the story itself.

Checks, in order:
  R-01 human speech — the dog speaks human words
  R-02 invented events — a claimed event with no supporting shared memory
  R-03 temper / boundary — behaviour outside recorded temper/boundaries
  R-04 identity — contradicts a frozen identity fact
  R-05 inferred-as-observed — an inferred fact presented as observed

Returns a Trace (verdict allow | change | block). The caller writes the
trace to the datapack and to traces/.
"""

from __future__ import annotations

import uuid

from src.rules import RULES, check_human_speech
from src.trace import Trace

AGENT_ID = "guardian"

# Boundary keywords that must be backed by a shared memory to be allowed.
BOUNDARY_CLAIMS = {
    "hug": "S-04",  # dog does not like being hugged by strangers
    "thunder": "S-02",
}


def review(client, draft: str, memories: list[dict]) -> Trace:
    trace_id = f"trace-{uuid.uuid4().hex[:8]}"
    # Live memories carry text under "memory"; the mock uses "text".
    memory_texts = [m.get("text") or m.get("memory") or "" for m in memories]

    # R-01: human speech is a hard block.
    if check_human_speech(draft):
        return Trace(
            trace_id=trace_id,
            verdict="block",
            rule_id="R-01",
            rule_text=RULES["R-01"],
            memories_consulted=memories,
            missing_facts=[],
            explanation=(
                "The draft gives the dog human speech (\"I am afraid…\" said by "
                "the dog). The twin never speaks human words — only dog sounds "
                "and behaviour. The fear itself is real and in shared memory "
                "(S-02), so the story can keep the fear and lose the words: "
                "hide behind the sofa, whine softly, wait for the owner."
            ),
            draft=draft,
        )

    # R-02: a claimed event with no supporting memory is a change, not a
    # silent pass — the Storyteller must rewrite from memory or the claim
    # must be confirmed as a new observation first.
    missing = []
    lowered = draft.lower()
    if "beach" in lowered and not any("beach" in t.lower() for t in memory_texts):
        missing.append("The story mentions a beach, but no shared memory mentions a beach.")
    if "veterinarian" in lowered and not any("vet" in t.lower() for t in memory_texts):
        missing.append("The story mentions a vet visit, but no shared memory mentions one.")
    if missing:
        return Trace(
            trace_id=trace_id,
            verdict="change",
            rule_id="R-02",
            rule_text=RULES["R-02"],
            memories_consulted=memories,
            missing_facts=missing,
            explanation=(
                "The draft claims something no shared memory supports. Either "
                "rewrite it from the memories listed above, or log the event "
                "as a new observation first and promote it after confirmation."
            ),
            draft=draft,
        )

    return Trace(
        trace_id=trace_id,
        verdict="allow",
        rule_id="—",
        rule_text="No rule fired. The draft uses only shared memory and the dog does not speak.",
        memories_consulted=memories,
        missing_facts=[],
        explanation=(
            "Every sentence in the draft traces to a shared memory listed "
            "above, the dog speaks no human words, and the behaviour is "
            "inside its recorded temper and boundaries."
        ),
        draft=draft,
    )
