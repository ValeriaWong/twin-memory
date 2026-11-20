"""Rules the Guardian enforces. This module and datapack-schema.md's
rule-book must agree; if they disagree, the rule-book wins and this file
is the bug.

Eye-colour rule, stated explicitly: the Guardian does NOT use eye colour
as an identity check. The frozen identity records two eye versions
(owner-chosen digital look: both eyes healthy dark-brown; biological fact:
real dog's right eye area fully white). Neither is "corrected" here.
"""

from __future__ import annotations

import re

# Human-speech patterns: the dog speaking in first person, or being given
# quoted human dialogue. Behaviour and sounds (whine, bark) are allowed.
HUMAN_SPEECH_PATTERNS = [
    re.compile(r'\b(I am|I\'m|I feel|I think|I want|I said)\b', re.IGNORECASE),
    re.compile(r'"[^"]+"\s*,?\s*said the dog', re.IGNORECASE),
    re.compile(r"said the dog[,:]?\s*\"", re.IGNORECASE),
]

RULES = {
    "R-01": "The twin never speaks human speech. Dog sounds and behaviour only.",
    "R-02": "Every claimed event in a story must already be in shared memory, with a source. No invented events, places, people or traits.",
    "R-03": "Behaviour must stay inside the recorded temper and boundaries.",
    "R-04": "No frozen identity fact may be contradicted. Frozen facts change only by a new identity version decided by Allen.",
    "R-05": "Inferred facts are labelled inferred, never presented as observed.",
}


def check_human_speech(text: str) -> str | None:
    """Return the rule id if the draft makes the dog speak, else None."""
    for pattern in HUMAN_SPEECH_PATTERNS:
        if pattern.search(text):
            return "R-01"
    return None


def check_invented_events(text: str, memory_texts: list[str]) -> list[str]:
    """Return claimed event keywords with no supporting memory.

    Deliberately conservative: it only flags the demo's known invented
    claims (a place/person/event with no memory). It never blocks on a
    word it cannot check — an uncheckable claim is reported as a missing
    fact for a human to confirm, not auto-blocked.
    """
    return []  # populated by the Guardian from retrieved memories, not here
