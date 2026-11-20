"""Pluggable LLM. Default is an offline deterministic mock — no key, no cost.

A real free model can be plugged in later via env vars only (LLM_PROVIDER,
LLM_MODEL, LLM_API_KEY in .env, never in the repo). The adapter below is a
minimal HTTPS chat-completions-style client; verify the provider's current
endpoint and free-tier limit before use, and never exceed a free tier.
"""

from __future__ import annotations

import requests


class MockLLM:
    """Deterministic scripted text, so the demo is reproducible offline."""

    def __init__(self, model: str = "mock-llm") -> None:
        self.model = model

    def generate(self, prompt: str, system: str = "") -> str:
        if "rainy" in prompt.lower() or "thunder" in prompt.lower():
            return (
                "Rain drummed on the window. The dog hid behind the sofa and "
                "whined softly until the owner sat nearby, and then its curled "
                "tail thumped once, twice, against the floor."
            )
        return "The dog trotted to the door, tail curled and wagging, and gave a short happy bark."


class FreeModelLLM:
    """Minimal chat-completions client. Provider endpoint passed in by caller.

    This is intentionally thin: it does not hard-code any provider's quota or
    price, because those change. The caller (see README.md) must verify the
    free tier first. Raises if no key is configured.
    """

    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        if not api_key:
            raise ValueError("FreeModelLLM needs LLM_API_KEY in .env, not in source.")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, system: str = "") -> str:
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system or "You are a storyteller for a dog's digital twin."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def build_llm(cfg):
    if cfg.llm_provider in ("", "mock"):
        return MockLLM()
    # Any real provider needs an explicit base URL from the caller, not a
    # guessed default. Wire it here once the provider is chosen and verified.
    raise ValueError(
        f"LLM_PROVIDER={cfg.llm_provider!r} is not wired yet. Add its verified "
        "base URL and free-tier limit in src/llm.py, or use mock mode."
    )
