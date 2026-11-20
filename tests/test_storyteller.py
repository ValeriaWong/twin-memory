"""Storyteller tests: a story may only use memories that exist in the
datapack. Run: python -m pytest tests/ -q
"""

from src.agents import storyteller
from src.llm import MockLLM
from src.meko_client import MockMekoClient


def _seeded_client():
    client = MockMekoClient()
    client.memory_add(
        "The dog is afraid of thunder. When thunder sounds it hides behind the sofa.",
        "observer",
        {"sample_id": "S-02"},
    )
    client.memory_promote([client.private[-1]["memory_id"]], "observer")
    return client


def test_story_uses_retrieved_memory():
    client = _seeded_client()
    story = storyteller.draft_story(client, MockLLM(), "thunder rainy day story")
    assert story["memories"], "storyteller must retrieve at least one memory"
    assert "thunder" in story["draft"].lower() or "rain" in story["draft"].lower()


def test_story_with_no_memory_reports_weak_match():
    client = MockMekoClient()
    story = storyteller.draft_story(client, MockLLM(), "a rainy-day story")
    assert story["match_quality"] == "weak"
    assert story["memories"] == []
