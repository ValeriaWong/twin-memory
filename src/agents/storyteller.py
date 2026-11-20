"""Storyteller — generates exclusive stories ONLY from shared memory.

Flow: context_search the datapack for the prompt -> draft from the top
retrieved memories only -> hand the draft to the Guardian before it is
shown to anyone. It never invents an event, place, person or trait, and
it never lets the dog speak human words (the Guardian blocks that, but the
Storyteller is also required not to draft it in the first place — the
violating draft in the demo is deliberately constructed by the demo script
to test the Guardian, not by this module's normal path).
"""

from __future__ import annotations

AGENT_ID = "storyteller"


def draft_story(client, llm, prompt: str, limit: int = 5) -> dict:
    """Draft a story from shared memory. Returns draft + memories used."""
    result = client.context_search(prompt, AGENT_ID, limit=limit)
    raw = result.get("memory", []) if isinstance(result, dict) else []
    if not raw and isinstance(result, dict):
        # Live context_search nests the buckets under "results".
        raw = (result.get("results") or {}).get("memory", [])
    # Live items carry the text under "memory" with an "id"; the mock
    # uses "text" / "memory_id". Normalise so the Guardian and the demo
    # see one shape either way.
    memories = [
        {
            "memory_id": m.get("id", m.get("memory_id", "")),
            "text": m.get("text") or m.get("memory", ""),
            "score": m.get("score"),
        }
        for m in raw
    ]
    memory_text = "\n".join(f"- {m['text']}" for m in memories)
    full_prompt = (
        "Write a short story for the dog twin using ONLY these shared memories:\n"
        f"{memory_text}\n\nPrompt: {prompt}\n"
        "The dog never speaks human words. Use narration, dog sounds and behaviour only."
    )
    draft = llm.generate(full_prompt)
    return {"draft": draft, "memories": memories, "match_quality": result.get("match_quality")}


def draft_violating_story() -> str:
    """The demo's deliberate failure case. NOT produced by draft_story().

    Used only by src/demo.py Scene B to prove the Guardian blocks it.
    """
    return '"I am afraid of the thunder," said the dog. "Please stay with me."'
