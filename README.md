# Twin Memory — ContextCon Track 07

A shared-memory layer for a real dog's digital twin, with a Guardian that can
show its work. Built for **ContextCon: Remember Everything, Track 07 Best
auditability**. Solo entrant: Allen Xiao.

> This is a separable slice of the pet-twin project, not the twin app.
> No video generation, no training, no GPU. The demo runs offline in mock
> mode with zero keys; the live path talks to Meko over MCP.

## What it proves (in 30 seconds)

1. **Agent A learns something, Agent B reuses it** — the Observer logs that
   the dog is afraid of thunder; the Storyteller later writes a rainy-day
   story that respects that fear, without re-observing anything.
2. **The Guardian blocks and explains** — the Storyteller drafts a line
   where the dog speaks human words; the Guardian blocks it, names the rule,
   shows the memories it consulted, and explains why in plain language.

## Quick start (mock mode, no account, no key)

```bash
cd contextcon-pet
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # leave the Meko values blank for mock mode
python -m src.demo          # runs both demo scenes against the mock datapack
python -m pytest tests/ -q  # Guardian rule tests
python scripts/measure_tokens.py --runs 3
```

Expected output: both scenes pass, the Guardian blocks the human-speech
draft, and a decision trace is written to `traces/`.

## Live mode (Meko, still free)

Do this only when Allen has created the Meko account himself (see
`SUBMISSION-CHECKLIST.md`). Never paste a key into chat or a file that gets
committed.

1. Allen signs up at https://mekodata.ai/ (Free plan, $0, no credit card)
   and creates a datapack named `twin-memory` in the Meko web portal.
2. Allen generates an API key in **Settings > API Keys** (keys start with
   `mko_tkn_`, shown once) and puts it in his own `.env` — never in the repo.
3. Fill in `.env` (from `.env.example`):
   - `MEKO_API_KEY` — the key Allen generated.
   - `MEKO_DATAPACK_ID` — the `twin-memory` datapack id from the portal
     (or its name; the client sends it on every tool call).
   - `MEKO_MCP_URL` — leave as `https://mcp.mekodata.ai/mcp`.
   - `MEKO_MODE=live`
4. Seed the datapack (synthetic sample data only — no real private videos):
   `python -m src.seed --mode live`
5. Run the demo: `python -m src.demo --mode live`
6. Check usage afterwards: the Free tier allows 1,000 conversations and
   10,000 retrievals per month; the demo uses a handful of each. If a quota
   is exceeded, Meko blocks further calls until upgrade — the demo must stay
   well inside the free limits, and it does (see `scripts/measure_tokens.py`
   output and `PLAN.md`).

### Alternative: OAuth, no key

In an MCP client that supports it (e.g. Claude Desktop's custom connector),
add the MCP server at `https://mcp.mekodata.ai/mcp` and complete the OAuth
handshake in the browser. Do **not** use OAuth from a plain terminal client:
clients with a local `http://127.0.0.1` callback get an HTTP 403 (Meko docs).
For the terminal demo, use the API key route above.

## How the code is organised

```
contextcon-pet/
  PLAN.md                  architecture, datapack design, judging map
  README.md                this file
  datapack-schema.md       exact datapack structure + synthetic sample data
  demo-script.md           timed <5 min demo, narration + on-screen proof
  SUBMISSION-CHECKLIST.md  what is still missing before 2027-01-17
  .env.example             config keys, NO real values
  requirements.txt         stdlib + requests + pytest only
  data/
    sample_memories.json   synthetic shared-memory seed (text only)
    sample_events.jsonl    synthetic observation events (text only)
  src/
    config.py              env-only config, refuses baked-in keys
    meko_client.py         MCP client (live) + in-memory mock (offline)
    llm.py                 pluggable LLM: offline MockLLM default, free-model adapter
    trace.py               decision-trace logger (JSON + readable text)
    rules.py               identity / speech / temper / boundary rules
    agents/
      observer.py          logs events, never judges or invents
      storyteller.py       drafts ONLY from shared memory
      guardian.py          verdict + trace, never rewrites the story
    demo.py                runs Scene A + Scene B end to end
    seed.py                seeds the datapack from data/sample_*.json*
  scripts/
    measure_tokens.py      baseline (stuff full context) vs Meko retrieval
  tests/
    test_guardian.py       a violating draft MUST be blocked
    test_storyteller.py    a story may only use memories that exist
  traces/                  decision traces written by demo runs (gitignored)
```

## Free-model notes

The demo does not need any paid model. It ships with an offline `MockLLM`
that returns deterministic, scripted text so the audit story is reproducible.

If a real model is wanted for the recorded demo, plug one in through env
vars only (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY` in `.env`, never in
the repo). Candidates to verify against Allen's free-API ledger at the time
— quotas change, so re-check before recording, and never exceed a free tier:

- **Gemini Developer API (Google AI backend)** — free tier, no billing
  required; the lightweight flash model is the usual pick for this kind of
  short generation. Verify the current free-tier rate limit before use.
- **Groq** — free tier with fast inference; verify the current model list
  and limits before use.
- **Cohere** — free tier; verify before use.

Do **not** use any model that needs a card, a trial that converts to paid,
or a key stored anywhere except Allen's own `.env`. If no free model is
available on recording day, record with `MockLLM` and say so on screen —
a scripted demo with a real Meko datapack behind it is honest; a demo that
pretends a paid model was free is not.

## The frozen identity, and the eye flag

Identity: `twinpet_001`, confirmed 2026-11-04, from
`~/workspace/ita-character-gen/characters/twinpet_001.json`. Cream-white
coat, irregular light-tan markings, asymmetric semi-folded ears, white
curled tail.

**Eye discrepancy — read PLAN.md before touching this.** The frozen file's
digital appearance is healthy dark-brown eyes for both eyes, chosen by the
owner as a digital look, not extracted from frames. The real dog's right eye
area is fully white. The Guardian does not use eye colour as an identity
check and does not "fix" either version. Changing the eye rule needs Allen's
explicit decision and a new identity version.

## Rules the code enforces

- The twin never speaks human speech. Only dog sounds and behaviour.
- Stories use only events already in shared memory, with a source.
- Interaction is sampling with personality constraints, never fixed branches.
- Promotion from private memory to shared memory is one-way and needs
  explicit confirmation (Meko `memory_promote`); the code never promotes
  automatically.
- No key, no private video, no real pet media in this repo. Sample data is
  synthetic text.

## Submission checklist

See `SUBMISSION-CHECKLIST.md`. In short: Meko account/key (Allen),
GitHub repo under ValeriaWong (Allen), demo video (<5 min, recorded from
`demo-script.md`), then submit on HackerEarth before 2027-01-17 23:59 PT.
