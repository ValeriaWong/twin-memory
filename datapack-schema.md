# Datapack schema — `twin-memory`

## Datapack

- **Name:** `twin-memory`
- **Purpose:** the single shared context for the pet-twin memory layer.
  One datapack, three agents, no side copies.
- **Created by:** Allen, in the Meko web portal (see SUBMISSION-CHECKLIST.md).
  The scaffold never creates it.
- **Free-tier budget (official Meko docs, verified 2026-11-20):** 10 datapacks
  per account, 100 MB knowledge storage, 1,000 conversations/month,
  10,000 retrievals/month, 10M WorkbenchLM tokens, 5 MB max per uploaded
  file. No contradiction between the docs pages: the homepage lists
  datapacks + knowledge + "$0, no credit card"; the datapacks doc adds
  conversations + WorkbenchLM tokens; the MCP-server doc adds retrievals.
  The demo uses 1 datapack, a handful of conversations and retrievals, and
  a few KB of knowledge — far inside every limit.

## What goes where

Rule of thumb: **conversations are the record, memory is the durable fact,
knowledge is the shared document, artifacts are the whole file, traces are
the proof.**

| Layer | Content | Who writes | Promotion / visibility |
|---|---|---|---|
| Conversations | Every agent turn, verbatim. Observer logs, Storyteller drafts, Guardian verdicts. Meko extracts durable facts from saved user turns automatically (`conversation_add_message`). | All three agents, each with its own `agent_id` | Visible to all agents on the datapack (conversation bucket in `context_search`) |
| Memory — private | Unconfirmed observations, per-agent working notes, a draft that has not been checked yet. Example: "ear tip looks higher in frame 62 — unconfirmed". | The agent that observed it | Private to the writing agent's namespace until promoted |
| Memory — shared (promoted) | Durable, confirmed facts only: frozen identity facts, learned preferences ("afraid of thunder"), boundaries ("never speak human words", "no hugging from strangers"). | Only via `memory_promote`, by the datapack owner/maintainer, after previewing the exact memories and getting explicit confirmation. **One-way: promotion removes the memory from the private store.** The code never promotes automatically. | Visible to every agent; this is what the Storyteller is allowed to use |
| Knowledge | Documents, searched by hybrid search: `identity-summary.md`, `rule-book.md`, `story-bible.md` (see below). | Seeded once by `src/seed.py` via `knowledgebase_upload_document`; updated only by Allen / the Guardian's confirmed corrections | Datapack-wide |
| Artifacts | Whole files: decision traces (`trace-*.json` + readable `.md`), story drafts, token-measurement reports. Use artifacts, not knowledge, when the file must come back whole instead of as retrieved passages. | Guardian (traces), Storyteller (drafts), `measure_tokens.py` (reports) | Datapack-wide, versioned by filename |
| Decision traces | Reasoning + tool calls + tokens behind each Guardian verdict. Stored twice: as an artifact (whole file) and as a conversation turn (so it is searchable). Token spend per verdict is also recorded with `track_token_usage`. | Guardian via `src/trace.py` | Datapack-wide |
| Self-learning | Meko's own report on which searches came back weak and what is missing (`selflearning_status`, `selflearning_shortfalls`, `selflearning_verify`). Checked at the end of each demo run; a gap found becomes a to-do, not a silent failure. | Meko (read by the demo) | Datapack owner/maintainer |

## Meko tools used (exact names from docs.mekodata.ai/reference/mcp-server/)

- `context_search` — open-ended recall across memory, knowledge base and
  past conversations in parallel; results in separate `memory`,
  `knowledge_base`, `conversation` buckets, with a `match_quality` band and
  an `agent_hint`. `force_source` can limit it to one bucket.
- `conversation_create`, `conversation_add_message`, `conversation_get`,
  `conversation_list` — the conversation record.
- `memory_add`, `memory_search`, `memory_get_all`, `memory_get_by_id`,
  `memory_update`, `memory_promote` — durable facts. Note: `memory_add`
  stores text as written with no duplicate check; prefer conversation
  capture and let Meko extract facts. `memory_promote` is one-way.
- `knowledgebase_upload_document`, `knowledgebase_search`,
  `knowledgebase_document_status` — documents (5 MB/file cap on Free).
- `artifact_put` / artifact retrieval — whole files (see note below).
- `track_token_usage` — record token spend against a conversation trace.
- `selflearning_status`, `selflearning_query_log`,
  `selflearning_shortfalls`, `selflearning_verify` — search-quality loop.
- `datapack_list` — verify the datapack exists before the demo runs.

Note on artifact tools: the MCP reference page groups tools as
`artifact_*` ("Uploading and retrieving files … for later or cross-agent
access") without spelling out every artifact tool name in the excerpt
verified on 2026-11-20. `src/meko_client.py` therefore treats artifact
writes as **optional**: it tries the documented artifact tool, and if the
live server does not expose it under that name, it falls back to storing the
trace as a conversation turn + a local file under `traces/`, and says so in
the output. The demo never claims an artifact write succeeded when it did
not. Before recording, re-check the live tool list with
`datapack_list` / the MCP tool list and pin the exact name in code.

## Knowledge documents (seeded, text only)

### `identity-summary.md` (knowledge)

A short summary of the frozen identity, copied from
`twinpet_001.json` — not a new decision:

- twinpet_001, pet_id twinpet_dog_001, confirmed 2026-11-04.
- Cream-white coat, irregular light-tan markings; lean, lightweight;
  asymmetric semi-folded ears; mostly-white curled tail; white muzzle,
  black nose.
- **Eyes — two versions, both recorded, neither silently resolved:**
  digital appearance (owner-chosen, both eyes healthy dark-brown) vs
  biological fact (real dog's right eye area fully white, no dark-brown
  stripe). The Guardian does not use eye colour as an identity check.
- Limits: 4 frames only, 480x360, no pure front view, t10 lower half
  blocked by a sheet.

### `rule-book.md` (knowledge)

The rules the Guardian enforces (also in `src/rules.py` — the code and the
document must agree; if they disagree, the document wins and the code is a
bug):

1. The twin never speaks human speech. Dog sounds and behaviour only.
2. Every claimed event in a story must already be in shared memory, with a
   source. No invented events, places, people or traits.
3. Behaviour must stay inside the recorded temper and boundaries.
4. No identity fact may be contradicted. Frozen facts change only by a new
   identity version decided by Allen.
5. Inferred facts are labelled inferred, never presented as observed.
6. Promotion private → shared is one-way and needs explicit confirmation.

### `story-bible.md` (knowledge)

The permitted story world: the dog, the owner, the home, the park from
sample memory S-03. The sampling set for next beats (not fixed branches):
greet / explore / rest / play / hide-from-thunder / seek-owner. Each beat
lists its temper preconditions (e.g. `hide-from-thunder` requires the
thunder-fear memory).

## Synthetic sample memory set

**All of this is invented sample text, written for the demo. It is not the
real dog's history and must never be presented as such.** It is based only
on the frozen identity (coat, ears, tail) plus generic dog behaviour. No
real private video, frame, audio or owner detail is used. The real datapack
is seeded from `data/sample_memories.json` (same content, machine-readable).

| ID | Text (shared memory, promoted) | Source | Type |
|---|---|---|---|
| S-01 | twinpet_001 is a cream-white dog with irregular light-tan markings, asymmetric semi-folded ears, and a mostly-white curled tail. | frozen identity twinpet_001, 2026-11-04 | identity |
| S-02 | The dog is afraid of thunder. When thunder sounds it hides behind the sofa and whines softly until the owner sits nearby. | synthetic sample event E-02 | learned preference / boundary |
| S-03 | The dog's favourite walk is the small park two streets from home, in the morning. | synthetic sample event E-03 | learned preference |
| S-04 | The dog does not like being hugged by strangers. It steps back and looks at the owner. | synthetic sample event E-04 | boundary |
| S-05 | The dog's name in stories is the twin's name only; the owner is "the owner". No other people are named in stories unless a shared memory names them. | rule-book (governance) | governance |
| S-06 | The dog greets the owner at the door with a wagging curled tail and a short happy bark. | synthetic sample event E-01 | learned behaviour |
| S-07 | On a rainy day with thunder, the dog hides behind the sofa and whines softly until the owner sits nearby; when the rain eases it goes to the window to watch the rain. | synthetic sample event E-02 + P-01 (bridging memory) | learned behaviour |

Private (unpromoted) sample, for the promotion demo:

| ID | Text (private, Observer only) | Status |
|---|---|---|
| P-01 | The dog seemed to watch the rain from the window for a long time this morning — unconfirmed, single observation. | Private. The demo promotes it only after Allen/the presenter confirms it on screen, showing the one-way `memory_promote` step. |

## Synthetic sample events (`data/sample_events.jsonl`)

Short text events, one per line, each with `event_id`, `timestamp`,
`source`, `confidence` (`observed` / `inferred`), and `text`. E-01 to E-04
back S-02/S-03/S-04/S-06. No media, no real timestamps from the real dog's
videos — the timestamps are demo placeholders.

## Seeding

`python -m src.seed` (mock mode by default) loads `data/sample_memories.json`
into the mock datapack and writes the three knowledge documents. In live
mode (`--mode live`) it calls the same Meko tools listed above against the
real `twin-memory` datapack. Seeding is idempotent in mock mode; in live
mode it checks `memory_search` first and skips facts already present (Meko
does no duplicate check on `memory_add`, so the seed script must).
