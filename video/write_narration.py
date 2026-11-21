#!/usr/bin/env python3
"""Write the 10 narration segments (script's exact wording) to txt files."""
from pathlib import Path

SEGMENTS = {
    "seg01": "This is Twin Memory. One Meko datapack, three agents, one real dog. The dog is twinpet_001. Nothing here is a video generator and nothing is trained — this is only memory, and whether that memory can be trusted.",
    "seg02": "The Observer just watched a storm. It logs one fact: the dog is afraid of thunder, and hides behind the sofa until the owner sits nearby. That fact goes into shared memory — after an explicit promotion, because promotion in Meko is one-way. The frozen identity uses healthy dark-brown eyes as the owner's chosen digital look. The real dog's right eye is fully white. We record both, and we do not use eye colour to check identity.",
    "seg03": "Now a different agent, the Storyteller, has never seen a storm. I ask it for a rainy-day story. It does not guess. It searches the datapack first.",
    "seg04": "The story it writes uses the thunder fear, the sofa, the owner sitting nearby — all things already in memory. Nothing invented. That is the whole point: one agent's learning, available to the next agent, without relearning.",
    "seg05": "Now the failure case. I ask the Storyteller for a story where the dog explains, in words, why it is afraid. That is the one thing this twin must never do.",
    "seg06": "The Guardian checks it. Rule one: the twin never speaks human speech. Rule two: every claimed event must already be in shared memory. The draft fails rule one.",
    "seg07": "Here is the trace. It names the rule, the memories, and the reason — in plain language, in under two minutes. Anyone can replay it.",
    "seg08": "The Storyteller rewrites from the trace — the Guardian never rewrites the story itself. The new version keeps the fear, loses the words.",
    "seg09": "One datapack. Three agents. The memory is shared, the rules are visible, and every decision leaves a trace you can replay.",
    "seg10": "Twin Memory. Built for ContextCon, Track 07. The code is public; the dog's real videos are not in it.",
}

out = Path(__file__).resolve().parent / "narration"
out.mkdir(exist_ok=True)
for name, text in SEGMENTS.items():
    (out / f"{name}.txt").write_text(text, encoding="utf-8")
    print("wrote", name, len(text), "chars")
