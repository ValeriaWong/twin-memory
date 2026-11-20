"""Guardian rule tests. A violating draft MUST be blocked; a clean draft
built from shared memory MUST be allowed. Run: python -m pytest tests/ -q
"""

from src.agents import guardian


def _mem(text, mid="S-02"):
    return [{"memory_id": mid, "text": text, "score": 0.95}]


def test_human_speech_is_blocked():
    trace = guardian.review(
        client=None,
        draft='"I am afraid of the thunder," said the dog.',
        memories=_mem("The dog is afraid of thunder."),
    )
    assert trace.verdict == "block"
    assert trace.rule_id == "R-01"
    assert "never speaks human words" in trace.explanation


def test_clean_story_is_allowed():
    trace = guardian.review(
        client=None,
        draft="Rain drummed on the window. The dog hid behind the sofa and whined softly.",
        memories=_mem("The dog is afraid of thunder. When thunder sounds it hides behind the sofa and whines softly."),
    )
    assert trace.verdict == "allow"


def test_invented_beach_is_change_not_silent_pass():
    trace = guardian.review(
        client=None,
        draft="The dog ran along the beach at sunset.",
        memories=_mem("The dog is afraid of thunder."),
    )
    assert trace.verdict == "change"
    assert trace.rule_id == "R-02"
    assert trace.missing_facts
