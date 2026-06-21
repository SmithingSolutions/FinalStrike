# EvalForge

A standalone Python orchestrator that mirrors **only the testing workflow** of Cursor cloud agents — environment bootstrap, build/lint gates, terminal tests, API checks, and computer-use UI verification — running on self-hosted GUI VMs and producing Cursor-parity evidence bundles.

## Architecture

EvalForge is an **orchestrator + evidence recorder**, not a test framework. It runs the same commands a Cursor cloud agent would run, uses an LLM to translate acceptance criteria into a verification plan, drives the UI like computer-use does, and packages proof.

```
CLI → Config Loader → AC Parser → LLM Test Planner
                          ↓
    Env Orchestrator → Build/Lint → Terminal Tests → API Checks → Computer-Use
                          ↓
              Evidence Recorder → Gap Analyzer → HTML Report
```

### Components

| Component | Responsibility |
|-----------|----------------|
| **CLI** | Typer entrypoints (`validate-config`, `plan`, `run`, `env`) |
| **Config Loader** | `evalforge.yaml`, `AGENTS.md`, `.cursor/environment.json`, secrets vault |
| **LLM Test Planner** | Acceptance criteria → structured `VerificationPlan` via OpenAI-compatible API |
| **Env Orchestrator** | `environment.json` install/terminals, health-check polling |
| **Command Runners** | Build/lint, terminal tests (pytest first), HTTP API checks |
| **Computer-Use Executor** | Screenshot + a11y → LLM action → OS input → evidence |
| **Evidence Recorder** | Desktop video, per-step screenshots, `RunResult` JSON |
| **Reporters** | HTML report (primary), Slack bot (deferred) |

Full design, data models, and phased implementation plan: **[PLAN.html](PLAN.html)**.

## Quick start

```bash
# Install in development mode
pip install -e ".[dev]"

# Validate fixture repo config
evalforge validate-config --repo fixtures/sample-app

# Dry-run plan: merged config + acceptance criteria (no LLM yet)
evalforge plan --repo fixtures/sample-app --acceptance fixtures/sample-app/acceptance.md --dry-run

# Start fixture services (install + terminals + health check)
evalforge env up --repo fixtures/sample-app
evalforge env down --repo fixtures/sample-app

# Run build + terminal layers; prints RunResult JSON
evalforge run --repo fixtures/sample-app \
  --acceptance fixtures/sample-app/acceptance.md \
  --layers build,terminal

# Accept criteria from stdin (e.g. piped PR body)
echo "## AC\n- item" | evalforge plan --repo fixtures/sample-app --acceptance-stdin --dry-run

# Export JSON schemas from Pydantic models
python -m evalforge.config.export_schemas
```

## Project layout

```
evalforge/          # Python package
fixtures/sample-app/  # Integration test target repo
schemas/            # Exported JSON schemas
tests/              # Unit and integration tests
PLAN.html           # Implementation plan
```

## Status

**Phase 0 (P0)** — project foundation: package scaffold, Pydantic models, JSON schemas, `validate-config` CLI, and fixture repo.

**Phase 1 (P1)** — config and context loading: `evalforge.yaml`, `AGENTS.md`, `.cursor/environment.json`, secrets vault, acceptance criteria, and `evalforge plan --dry-run`.

**Phase 2 (P2)** — environment orchestrator: `evalforge env up/down`, install/terminals from `environment.json`, HTTP health polling, process teardown.

**Phase 3 (P3)** — build/lint and terminal test runners: `evalforge run --layers`, pytest output parsing, `RunResult` JSON written under `.evalforge/runs/`.

See [PLAN.html](PLAN.html) section 8 for the full phase roadmap.

## License

MIT
