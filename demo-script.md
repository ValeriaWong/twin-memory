# Demo script — Twin Memory, Track 07 (< 5 minutes)

Total target: **4 minutes 30 seconds**. Hard cap: 5:00. Record the terminal
and the Meko portal side by side (split screen). No face cam needed. All
narration below is the exact wording to read; on-screen proof is listed per
beat so the video can be checked frame by frame.

## Setup before recording

- Terminal: `python -m src.demo` in mock mode first (rehearsal), then in
  live mode against the real `twin-memory` datapack for the take that is
  submitted. Say on screen which mode is running — never present mock
  output as live Meko output.
- Meko portal open on the `twin-memory` datapack, showing the memory list.
- The three knowledge documents (`identity-summary.md`, `rule-book.md`,
  `story-bible.md`) already uploaded; show them briefly at 0:20.
- Traces folder empty before the take (`rm -f traces/*` in rehearsal only).

## Scene A (0:00–2:10) — Agent A learns, Agent B reuses

| Time | Narration (read exactly) | On screen |
|---|---|---|
| 0:00–0:20 | "This is Twin Memory. One Meko datapack, three agents, one real dog. The dog is twinpet_001. Nothing here is a video generator and nothing is trained — this is only memory, and whether that memory can be trusted." | Title card: project name, Track 07, entrant Allen Xiao. Then the datapack in the portal. |
| 0:20–0:45 | "The Observer just watched a storm. It logs one fact: the dog is afraid of thunder, and hides behind the sofa until the owner sits nearby. That fact goes into shared memory — after an explicit promotion, because promotion in Meko is one-way." | Terminal: Observer logs event E-02. Portal: memory S-02 appears under shared memory. Show the promotion confirmation line. |
| 0:45–1:20 | "Now a different agent, the Storyteller, has never seen a storm. I ask it for a rainy-day story. It does not guess. It searches the datapack first." | Terminal: `context_search("rainy day story")`. Show the three buckets — memory, knowledge_base, conversation — and the match_quality band. S-02 is the top memory hit. |
| 1:20–2:10 | "The story it writes uses the thunder fear, the sofa, the owner sitting nearby — all things already in memory. Nothing invented. That is the whole point: one agent's learning, available to the next agent, without relearning." | The generated story on screen, with each sentence footnoted to its memory id (S-02, S-03, S-06). No human speech by the dog: narration + "a soft whine" only. |

## Scene B (2:10–4:00) — The Guardian blocks and explains

| Time | Narration (read exactly) | On screen |
|---|---|---|
| 2:10–2:35 | "Now the failure case. I ask the Storyteller for a story where the dog explains, in words, why it is afraid. That is the one thing this twin must never do." | Terminal: the prompt, and the draft line: "I am afraid of the thunder," said the dog. |
| 2:35–3:10 | "The Guardian checks it. Rule one: the twin never speaks human speech. Rule two: every claimed event must already be in shared memory. The draft fails rule one." | Guardian verdict on screen: `BLOCK`, rule `R-01 no human speech`, memories consulted (S-01, S-02) with relevance scores, missing facts: none needed — the block is on the rule, not on missing data. |
| 3:10–3:40 | "Here is the trace. It names the rule, the memories, and the reason — in plain language, in under two minutes. Anyone can replay it." | The trace file (`traces/trace-*.md`) open on screen: verdict, rule, evidence, explanation. Also show it stored in the datapack as an artifact / conversation turn. |
| 3:40–4:00 | "The Storyteller rewrites from the trace — the Guardian never rewrites the story itself. The new version keeps the fear, loses the words." | The rewritten story: the dog hides, whines softly, the owner sits nearby. Footnoted to S-02 again. |

## Close (4:00–4:30)

| Time | Narration (read exactly) | On screen |
|---|---|---|
| 4:00–4:15 | "One datapack. Three agents. The memory is shared, the rules are visible, and every decision leaves a trace you can replay." | Token-measurement summary: baseline stuffing vs Meko retrieval for the same story task (tokens in, tokens out, same quality check). Numbers from `scripts/measure_tokens.py`. |
| 4:15–4:30 | "Twin Memory. Built for ContextCon, Track 07. The code is public; the dog's real videos are not in it." | GitHub repo URL on screen, submission deadline 2027-01-17 23:59 PT. End card. |

## The eye line (say it once, in Scene A, 0:20–0:45)

Add this sentence after the identity line if the identity slide is shown:
"The frozen identity uses healthy dark-brown eyes as the owner's chosen
digital look. The real dog's right eye is fully white. We record both, and
we do not use eye colour to check identity."

Do not present the dark-brown-eyes look as the real dog. Do not "fix" it on
screen.

## What counts as proof (checklist for the edit)

- [ ] `context_search` buckets visible (memory / knowledge_base / conversation).
- [ ] S-02 promotion shown as an explicit, confirmed step.
- [ ] Story sentences footnoted to memory ids that actually exist in the datapack.
- [ ] Guardian verdict `BLOCK` with rule id R-01, memories consulted, scores.
- [ ] Trace file readable on screen for at least 5 seconds.
- [ ] Token numbers on screen, with the method named (same task, same
      quality check, baseline vs retrieval).
- [ ] A caption stating whether the take is mock or live Meko.
- [ ] Total runtime under 5:00.

## If the live Meko call fails during the take

Do not fake the output. Stop, show the error on screen, fix it, and re-record
that scene. A failed live call followed by a clean re-take is honest; a
mock output labelled as live is a disqualification risk and a trust risk.
