# AGENTS.md

## Cursor Cloud specific instructions

FinalStrike is a single Python package (`finalstrike`) exposing a Typer CLI. `fixtures/sample-app/` is the integration test target repo (not a separate product). Python 3.12 is used.

### Environment
- Dependencies are installed into a project virtualenv at `.venv` (gitignored). Activate with `source .venv/bin/activate` or prefix commands with `.venv/bin/` (e.g. `.venv/bin/pytest`, `.venv/bin/finalstrike`). The update script keeps `.venv` in sync.
- The test suite needs a gitignored local secrets vault at `fixtures/sample-app/.finalstrike/secrets.env` containing fake values `OPENAI_API_KEY=fixture-test-key-not-real` and `SLACK_BOT_TOKEN=fixture-slack-token`. Without it, 6 tests in `tests/test_p1_context.py` fail. The update script recreates it if missing.

### Phase gaps (P4+)

Before starting P4+, run `finalstrike doctor --repo fixtures/sample-app` and read
`docs/PHASE_GAPS.md`. The fixture uses `acceptance-smoke.md` for P0–P4 work and
`acceptance-full.md` for future P5/P6 demos; `capabilities.yaml` tracks what is
implemented vs planned.

### Lint / test / build / run
- Tests: `pytest -q` (config in `pyproject.toml` `testpaths = ["tests"]`). Run with the venv **activated** (`source .venv/bin/activate`) so `.venv/bin` is on `PATH`. The orchestrator's terminal-layer tests spawn a bare `pytest` subprocess, so invoking the suite as `.venv/bin/pytest` (without activation) leaves `pytest` off `PATH` and makes 3 tests in `tests/test_p3_runners.py` fail with `pytest: not found`.
- Lint: no linter is configured (dev deps are pytest only); there is nothing to run.
- Build/run the app: it is a CLI, not a server. Core commands: `finalstrike --version`, `finalstrike doctor --repo fixtures/sample-app`, `finalstrike validate-config --repo fixtures/sample-app`, `finalstrike plan --repo fixtures/sample-app --acceptance fixtures/sample-app/acceptance-smoke.md --dry-run`, and `finalstrike run --repo fixtures/sample-app --acceptance fixtures/sample-app/acceptance-smoke.md --layers api` (with services up). See `README.md` Quick start.
- Regenerate JSON schemas: `python -m finalstrike.config.export_schemas` (writes to `schemas/`; output is committed and currently up to date).
- The `fixtures/sample-app` server (integration target) runs via `python -m sample_app.server 8080` from inside `fixtures/sample-app/` and serves `GET /health` -> `200 ok`.

### Live LLM testing (external API)
- LLM config is read from `fixtures/sample-app/finalstrike.yaml` under `llm:` (`provider: openai_compat`, `base_url`, `model`). The transport is a single OpenAI-compatible client, so any gateway works by setting `base_url`/`model` (OpenAI `https://api.openai.com/v1`, OpenRouter `https://openrouter.ai/api/v1`, LiteLLM proxy, etc.). The committed fixture points at a local Ollama example (`http://localhost:11434/v1`, `llama3`); no local LLM server is installed on this VM.
- The API key resolves from the vault (`OPENAI_API_KEY` in `fixtures/sample-app/.finalstrike/secrets.env`) first, then the process env. Live external-API testing requires adding a real `OPENAI_API_KEY` as a Cloud Agent secret. Outbound HTTPS egress works (`https://api.openai.com/v1/models` returns 401 without a key; `https://openrouter.ai/api/v1/models` returns 200), and the `openai` SDK is installed in `.venv`.
- GOTCHA — do NOT overwrite the committed fixture vault with a real key. `tests/test_p1_context.py::test_load_secrets_from_sample_app` hard-asserts `OPENAI_API_KEY == "fixture-test-key-not-real"`, so replacing the vault value (e.g. from an install/update script) breaks `pytest -q`. For live runs, supply the real key via the process env (`OPENAI_API_KEY=... finalstrike ...`) — env-var resolution already covers this — rather than editing the fixture vault.
- STATUS — the live LLM planner (Phase 5) is NOT implemented. `finalstrike/planner` and `finalstrike/providers/openai_compat.py` are empty stubs, so `finalstrike plan --no-dry-run` only prints the merged context with a "LLM planner is not implemented yet" note and makes no API call. There is no `finalstrike doctor` command, no `generate_verification_plan`, no `fixtures/sample-app/acceptance-smoke.md`, no `tests/test_p5_*`, and no `docs/PHASE_GAPS.md`/`tests/llm_recordings/`. Until P5 lands there is no code path that calls the external API, so an end-to-end live planner run cannot be verified.
