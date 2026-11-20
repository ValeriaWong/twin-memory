# ContextCon: Remember Everything — Twin Memory (Track 07, Best Auditability)

## What this is

A separable memory layer for Allen's real-pet digital twin — not the full twin
app, not a video generator, not a training run. Three small agents share one
Meko datapack. One agent's learning becomes every agent's advantage, and
every decision that touches the dog's identity can be traced and explained in
under two minutes.

- Entrant: Allen Xiao (Xiao Allen), geekxl15@gmail.com, solo.
- Registered: 2026-11-20 on HackerEarth, team "Allen's Team", 1 member.
- Track: **07 Best auditability** ("Show Your Work"). Secondary target: the
  **Best use of shared memory** special award ($1,000).
- Submission deadline: **2027-01-17 23:59 PT** (2027-01-18 15:59 Beijing time).
- Submission: a demo video under 5 minutes + a public GitHub repo
  (+ optional docs). This scaffolding is the repo contents before the video.

## The product idea in one paragraph

A digital twin of a real dog must remember. It must remember the owner, past
play, what scared it, what it likes, and the hard boundaries of its
personality — and every agent working on the twin (the one watching video, the
one writing stories, the one rendering) must read from the same memory instead
of relearning the dog from scratch each session. Twin Memory is that shared
memory plus a guardian that enforces the dog's identity rules and can show its
work: which memories it used, which rule fired, and why it refused or changed
something.

## Frozen identity — read, not changed

Source: `~/workspace/ita-character-gen/characters/twinpet_001.json`
(`character_id: twinpet_001`, `identity_status: confirmed`,
`confirmed_at: 2026-11-04T12:41:55Z`, `pet_id: twinpet_dog_001`).
Evidence: 4 frames (bf3e_10 three-quarter front, 0550_t26 side standing,
0550_t10 back, 0550_t28 back-side sitting). Known limits recorded in the file:
frames are only 480x360, no pure front view, the lower half of t10 is blocked
by a sheet (markings there unconfirmed), bf3e_10 contains the owner's leg/foot.

Identity facts used here (copied from that file, not re-decided):

- Cream-white base coat, irregular light-tan markings (ears, around eyes,
  shoulders, back, torso); lean, lightweight, long-legged body.
- Ears naturally asymmetric, semi-folded.
- Tail mostly white, curled up; short to mid-short fur; white muzzle, black nose.

### FLAG — the eye discrepancy (do not silently fix)

The frozen file's `eyes_digital` is `both_like_healthy_dark_eye`, explicitly
marked `source: owner_preference` with the note "主人选择的数字外观，非从帧中提取"
(owner-chosen digital appearance, not extracted from frames), and the
`identity_description` ends: "数字外观版本（主人选择，非真实状态）：双眼均接近
健康眼睛的自然深棕色。"

The biological fact is different: **the real dog's right eye area is fully
white — no dark-brown stripe.** That is a hard identity feature.

Consequences for this project:

1. The Guardian must **never** use eye colour as an identity check, and must
   never "correct" the frozen digital appearance toward the real eye, or vice
   versa. Both versions are recorded, with their provenance, in the datapack
   (see `datapack-schema.md`).
2. Any change to the eye rule is a new identity version (twinpet_002 or later)
   and needs Allen's explicit decision. This scaffold does not create one.
3. The demo must not present the dark-brown-eyes digital look as the real
   dog's appearance. The narration line in `demo-script.md` states the
   distinction on screen.

## The three agents

All three share exactly one datapack (`twin-memory`, see
`datapack-schema.md`). They are identified by distinct `agent_id` values so
every write is attributable in the trace. No agent keeps a private copy of
the dog's facts; the datapack is the single source of truth.

### 1. Observer (`src/agents/observer.py`, agent_id `observer`)

Logs events and observations into the datapack. It never judges, never
invents, never writes stories.

- Inputs: short, human-readable observation records (in the demo and in
  tests: synthetic text events; in real use: the output of the existing
  ear-prelabel / whine-detection pipelines, summarised as text).
- Writes: a conversation turn via `conversation_add_message` (Meko then
  extracts durable facts automatically), plus an explicit `memory_add` only
  for durable facts the turn-extraction cannot reach (corrections, e.g.
  "the ear tip in frame 62 is X, not Y"). See the Meko skill rule: prefer
  conversation capture; `memory_add` is the exception, not the default.
- Every observation carries: timestamp, source (which pipeline / who saw it),
  confidence (observed vs inferred — inferred is always labelled as such),
  and the frame/event id it came from. No observation without a source.

### 2. Storyteller (`src/agents/storyteller.py`, agent_id `storyteller`)

Generates exclusive stories for the twin. Hard rule: **it may only use facts
already in shared memory.** It may not invent an event the dog never
experienced, a place it never visited, a person it never met, or a trait it
does not have.

- Flow: `context_search` the datapack for the story prompt → draft from the
  top retrieved memories only → hand the draft to the Guardian before it is
  shown to anyone → if the Guardian blocks or changes it, the draft is
  rewritten from the trace, not silently patched.
- The twin never speaks human speech. Stories are told in third-person
  narration plus dog sounds and behaviour (whine, bark, tail, ears, posture).
  A draft containing human dialogue spoken by the dog is a Guardian block,
  not an edit.
- Interaction is sampling with personality constraints, never fixed branches:
  the Storyteller samples a next beat from the permitted set given the dog's
  current temper, then the Guardian checks it. The permitted set is stored in
  knowledge, so it is shared and auditable, not hidden in code.

### 3. Guardian (`src/agents/guardian.py`, agent_id `guardian`)

Enforces personality, temper and boundary rules and outputs a readable
decision trace. It is the Track 07 core.

- Inputs: a proposed story beat / action + the memories the Storyteller
  relied on (retrieved via `context_search`, with relevance scores).
- Checks, in order: (a) identity — does it contradict a frozen identity fact?
  (b) experience — is every claimed event in shared memory, with a source?
  (c) speech — does the dog speak human words? (d) temper/boundary — is the
  proposed behaviour within the dog's recorded temper and boundaries?
- Output: a verdict (`allow`, `change`, `block`) + a decision trace
  (`src/trace.py`): the rule that fired, the exact memories consulted
  (with their Meko memory ids and relevance scores), the facts that were
  missing, and a plain-language explanation a non-technical person can read
  in under two minutes. The trace is written back to the datapack as an
  artifact (whole file, via `artifact_put`) and as a conversation turn, so
  the next agent can replay it.
- The Guardian never rewrites a story itself. It returns the verdict and the
  trace; the Storyteller does the rewrite. Separation of powers is the point.

## Meko datapack design

One datapack: `twin-memory`. Full schema in `datapack-schema.md`.

| Meko layer | What lives there | Meko tools |
|---|---|---|
| Conversations | Every agent turn, verbatim, so facts are extracted and replayable | `conversation_create`, `conversation_add_message`, `conversation_get`, `conversation_list` |
| Memory (private) | Per-agent working notes, unconfirmed observations | `memory_add`, `memory_search`, `memory_get_all` |
| Memory (shared) | Promoted durable facts: identity, learned preferences, boundaries. Promotion is one-way (`memory_promote`) and needs the datapack owner/maintainer plus explicit confirmation — the demo asks for it on screen, it is never automatic | `memory_promote` |
| Knowledge | Documents: the frozen identity summary, the rule book, the story bible. Hybrid search | `knowledgebase_upload_document`, `knowledgebase_search` |
| Artifacts | Decision traces, story drafts, token-measurement reports — stored whole, read back whole | `artifact_put`, `artifact_get` (see note in datapack-schema.md) |
| Decision traces | Reasoning + tool calls + tokens behind every Guardian verdict | `track_token_usage`, trace artifacts |
| Self-learning | Which searches came back weak, what is missing | `selflearning_status`, `selflearning_query_log`, `selflearning_shortfalls`, `selflearning_verify` |

## Architecture

```
                ┌─────────────────────────────┐
                │  Meko datapack "twin-memory" │
                │  memory · knowledge · convs  │
                │  artifacts · traces          │
                └──────┬──────────┬───────────┘
                       │ MCP      │ MCP
              ┌────────┴──┐  ┌────┴─────┐  ┌──────────┐
              │ Observer  │  │Storyteller│  │ Guardian │
              │ logs      │  │ drafts    │  │ verdicts │
              │ events    │  │ stories   │  │ + traces │
              └───────────┘  └────┬──────┘  └──────────┘
                                  │ draft for review
                                  └──────► Guardian
                                  ◄────── verdict + trace
```

- Transport: Meko Cloud MCP, one endpoint for every client
  (`https://mcp.mekodata.ai/mcp`). Auth is either OAuth (browser sign-in) or
  an API key (`mko_tkn_…`) sent as `Authorization: Bearer <key>` **plus**
  a `User-Agent` header — Meko rejects requests without either. The code in
  `src/meko_client.py` implements exactly that, and refuses to run with a key
  baked into source: config comes from environment variables only.
- LLM: pluggable (`src/llm.py`). The demo runs in **offline mock mode** with
  no key at all — deterministic, scripted outputs, so the audit story can be
  rehearsed and recorded without spending anything. A real free model can be
  plugged in later via env vars (see README.md); no key is ever committed.
- No GPU, no video generation, no training in this scaffold. The demo video
  is a screen recording of the terminal + datapack portal, with stills from
  the frozen identity evidence list (not the private video frames themselves).

## How each judging criterion is met

Judging (ContextCon official page): Meko use 30%, impact 25%, technical
execution 20%, innovation 15%, presentation 10%.

- **Meko use (30%) — the strongest card.** All six Meko layers are used
  (conversations, private→shared memory with an explicit promotion step,
  knowledge, artifacts, decision traces, self-learning). The demo shows a
  `context_search` returning separate memory / knowledge_base / conversation
  buckets, a `memory_promote` that is deliberately one-way and confirmed on
  screen, and a `selflearning_shortfalls` check that finds a gap and closes
  it. Nothing is faked with a local JSON file pretending to be Meko: the
  mock client is labelled mock, and the live path is the real MCP endpoint.
- **Impact (25%).** Real problem, real user: a twin that forgets its dog is
  a generic chatbot; a twin that remembers is a product. The demo proves
  reuse, not just storage: Agent B answers from Agent A's memory without
  re-observing, and the Guardian's block is a real user-protection outcome
  (the dog never speaks human words, boundaries are enforced).
- **Technical execution (20%).** Small, clean, runnable: one datapack, three
  modules, a trace logger, a token-measurement script, tests for the
  Guardian's rules (a violating draft must be blocked in tests, not just in
  the demo). Setup is `pip install -r requirements.txt`, copy
  `.env.example` to `.env`, run `python -m src.demo`.
- **Innovation (15%).** The fresh take is auditability as a feature of a pet
  product: the Guardian's trace is the product's trust surface, and the
  private→shared promotion ceremony makes "what the twin is allowed to
  remember" a visible, governed decision instead of a hidden prompt.
- **Presentation (10%).** The demo script (`demo-script.md`) is timed to
  under 5 minutes, two scenes, each with an on-screen proof (datapack search
  results, trace file, token numbers). No slides-only submission.

## What this scaffold deliberately does NOT do

- No GitHub repo is created here (Allen creates it under ValeriaWong).
- No Meko account or API key is created or recorded here (Allen creates it).
- No real private pet videos are copied into this repo. The sample data is
  synthetic text events based on the frozen identity.
- No GPU training, no video generation, no DPO, no ear/whine model runs.
  Those belong to the twin project and its GPU queue, not to this competition
  slice. This slice must stay separable: if ContextCon stopped tomorrow, the
  twin project would lose nothing except this demo.
- No new identity version. twinpet_001 stays frozen as read.

## Sources verified 2026-11-20 (all official Meko docs)

- MCP endpoint: `https://mcp.mekodata.ai/mcp` — "Every account and datapack
  connecting to Meko Cloud uses the same hosted endpoint URL" —
  docs.mekodata.ai/use-meko/connect/ and /reference/mcp-server/.
- Free tier (no contradiction found between the pages; the numbers below are
  the union of the official pages, each cited where it appears):
  - $0, no credit card; 10 datapacks; 100 MB knowledge storage —
    mekodata.ai pricing section.
  - 1,000 conversations/month and 10,000 retrieval requests/month
    (`context_search`, `memory_search`, `knowledgebase_search`) —
    docs.mekodata.ai/reference/mcp-server/ ("Free tier quotas") and
    /use-meko/connect/.
  - 10M WorkbenchLM tokens; per-file upload cap 5 MB on Free —
    docs.mekodata.ai/use-meko/datapacks/ and /reference/mcp-server/.
  - When a quota is exceeded, further calls are blocked until upgrade —
    /reference/mcp-server/.
- Auth: API keys start with `mko_tkn_`, shown once, long-lived; requests
  need `Authorization: Bearer <key>` **and** a `User-Agent` header; OAuth
  is the alternative (browser sign-in, no key) but fails for CLI clients
  with a local `http://127.0.0.1` callback (HTTP 403) — use the installer or
  an API key for those — /use-meko/connect/.
- Tools (32 documented): `context_search`, `conversation_create`,
  `conversation_add_message`, `conversation_get`, `conversation_list`,
  `conversation_update`, `conversation_delete`, `track_token_usage`,
  `memory_add`, `memory_search`, `memory_get_all`, `memory_get_by_id`,
  `memory_update`, `memory_delete_by_id`, `memory_delete_all`,
  `memory_promote`, `knowledgebase_search`,
  `knowledgebase_upload_document`, `knowledgebase_document_status`,
  `knowledgebase_delete_document`, `selflearning_status`,
  `selflearning_query_log`, `selflearning_shortfalls`,
  `selflearning_verify`, `datapack_*`, `artifact_*` —
  /reference/mcp-server/. `memory_promote` is one-way (private store →
  shared knowledge layer) and only datapack owners/maintainers may do it,
  after previewing the exact memories and getting explicit confirmation.
- `context_search` returns separate `memory`, `knowledge_base` and
  `conversation` buckets, a `match_quality` band and an `agent_hint` —
  /reference/mcp-server/.
- `conversation_add_message` asynchronously extracts durable facts from the
  saved user turn; repeated facts are dropped — /reference/mcp-server/.
- Datapack: "A datapack replaces the database, vector store, RAG pipeline,
  memory layer and conversation store" and holds memory, knowledge,
  decision traces and artifacts — docs.mekodata.ai (home).
- ContextCon rules relied on: every project must use Meko as its context
  layer; submission is a demo video under 5 minutes + public GitHub repo;
  judging weights as listed above; deadline 2027-01-17 23:59 PT —
  hackerearth.com/lp/challenges/contextcon (verified 2026-11-20).
