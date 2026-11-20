# Submission checklist — ContextCon, Twin Memory (Track 07)

Deadline: **2027-01-17 23:59 PT** (2027-01-18 15:59 Beijing time).
Submit on HackerEarth: demo video (< 5 min) + public GitHub repo + optional docs.

## Already done (in this scaffold, 2026-11-20)

- [x] PLAN.md — architecture, datapack design, judging map, verified Meko sources.
- [x] README.md — setup, mock + live modes, free-model notes.
- [x] datapack-schema.md — datapack structure, memory vs knowledge vs
      artifacts, synthetic sample data (no real private media).
- [x] demo-script.md — timed < 5 min script, two scenes, exact narration.
- [x] Python skeleton — Meko client (live MCP + offline mock), three agents,
      decision-trace logger, rules, token-measurement script, tests.
- [x] `.env.example` with no real values; `.gitignore` covering `.env`,
      `.venv/`, `traces/`, `__pycache__/`.
- [x] Frozen identity read from `twinpet_001.json`; eye discrepancy flagged
      in PLAN.md, README.md, datapack-schema.md and demo-script.md.
- [x] Meko docs verified (endpoint, free-tier limits, tool names, auth
      headers) — see PLAN.md "Sources verified".

## Still needs Allen (only Allen can do these)

- [ ] **Meko account** — Allen signs up at https://mekodata.ai/ (Free, $0,
      no credit card). No one else creates it; no key is recorded anywhere
      by anyone else.
- [ ] **Datapack `twin-memory`** — Allen creates it in the Meko web portal.
- [ ] **Meko API key** — Allen generates it in Settings > API Keys
      (starts `mko_tkn_`, shown once), puts it in his own `.env` only.
      If it is lost, revoke and regenerate; Meko cannot show it again.
- [ ] **GitHub repo** — Allen creates the public repo under **ValeriaWong**
      (name suggestion: `twin-memory`; if taken, `contextcon-twin-memory`),
      pushes this scaffold. No repo is created here.
- [ ] **LinkedIn / profile fields** — HackerEarth profile shows GitHub not
      connected and 5% complete (noted at registration). Optional: connect
      GitHub ValeriaWong in the HackerEarth profile. Not required to submit.
- [ ] **Free LLM choice (optional)** — if a real model is wanted for the
      recorded demo, Allen picks one from the free-API ledger and confirms
      its current free-tier limit. Otherwise record with the offline mock
      and say so on screen.

## Still needs building (before recording)

- [ ] Run the full demo in mock mode; all Guardian tests pass
      (`python -m pytest tests/ -q`).
- [ ] Seed the live datapack (`python -m src.seed --mode live`) and verify
      in the portal: S-01–S-06 shared, P-01 private, three knowledge docs
      uploaded and indexed (`knowledgebase_document_status` = completed).
- [ ] Confirm the exact artifact tool name on the live MCP server before
      recording (see datapack-schema.md note) and pin it in
      `src/meko_client.py` if it differs from the fallback.
- [ ] Run `scripts/measure_tokens.py` in live mode and paste the real
      numbers into the demo close (baseline vs Meko retrieval, same task).
- [ ] Check `selflearning_status` on the datapack after the rehearsal;
      close any gap it reports (add the missing fact once, re-run
      `selflearning_verify`).
- [ ] Record the demo from `demo-script.md` (live take preferred; mock take
      only if labelled mock on screen). Runtime under 5:00.
- [ ] Watch the finished video once, against the proof checklist in
      `demo-script.md`, before submitting.
- [ ] Submit on HackerEarth before 2027-01-17 23:59 PT. Keep a screenshot
      of the submission confirmation.

## Do not do

- Do not commit `.env` or any key. Do not paste a key into chat.
- Do not copy real private pet videos, frames or audio into the repo.
- Do not create a new identity version (twinpet_002) without Allen's decision.
- Do not pay for Meko Standard ($25/mo) or any model. If a free limit is
  hit, stop and report it — do not upgrade.
- Do not present mock output as live Meko output.
