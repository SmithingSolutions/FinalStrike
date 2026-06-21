# Local development setup

Follow this guide once per machine (or after pulling dependency changes) so
`pytest -q` and `finalstrike doctor` do not fail due to environment misconfiguration.

## Quick setup (recommended)

From the repository root:

```bash
./scripts/setup-dev.sh
source .venv/bin/activate
pytest -q
```

To **replace a broken `.venv`** (e.g. `pip: cannot execute: required file not found`
after moving the repo or upgrading Python):

```bash
./scripts/setup-dev.sh --recreate-venv
source .venv/bin/activate
pytest -q
```

## What the default test suite needs

| Requirement | Required for `pytest -q`? | Notes |
|-------------|---------------------------|-------|
| Python 3.11+ (3.12 recommended) | Yes | `python3 --version` |
| Project virtualenv at `.venv/` | Yes | Never use system `pip` on Debian/Ubuntu ([PEP 668](https://peps.python.org/pep-0668/)) |
| `pip install -e ".[dev]"` into `.venv` | Yes | Installs `finalstrike`, `pytest`, `mss`, etc. |
| Fixture secrets vault | For `doctor` only | `fixtures/sample-app/.finalstrike/secrets.env` must **exist** with `OPENAI_API_KEY` set (any value — real OpenAI key is fine) |
| `pytest` on `PATH` when running tests | Yes | **Activate** `.venv` before `pytest -q`, or use `.venv/bin/pytest` |
| Live LLM (Ollama, OpenAI, …) | No | Skipped; cassettes cover planner/computer-use in CI |
| Chrome/Chromium, `xdotool`, GUI display | No | Only for optional `@requires_platform_tools` tests |
| `ffmpeg` | No | Only for optional platform-tool tests |

**Expected default result:** `pytest -q` → all tests pass except a few **skipped**
(live LLM / platform tools when not configured). Example: `120 passed, 4 skipped`.

## Manual setup (step by step)

### 1. System packages (Debian/Ubuntu, once)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
# Match your Python minor version if needed, e.g.:
# sudo apt install -y python3.12-venv
```

### 2. Virtualenv — do not reuse a copied or stale `.venv`

```bash
cd /path/to/FinalStrike

# If .venv is missing OR pip/python inside it is broken:
rm -rf .venv
python3 -m venv .venv
```

Verify:

```bash
.venv/bin/python --version
.venv/bin/pip --version
```

If `pip` still fails, the venv was not created cleanly — delete `.venv` and retry
after installing `python3-venv`.

### 3. Install the package and dev dependencies

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

Without activating:

```bash
.venv/bin/pip install -e ".[dev]"
```

### 4. Fixture secrets vault (`doctor` and live CLI)

`finalstrike doctor --repo fixtures/sample-app` expects a secrets file to exist.
The default test suite does **not** require specific fake key values — you may use
your real OpenAI (or other provider) API key here.

```bash
mkdir -p fixtures/sample-app/.finalstrike
cat > fixtures/sample-app/.finalstrike/secrets.env <<'EOF'
OPENAI_API_KEY=your-real-or-placeholder-key
SLACK_BOT_TOKEN=fixture-slack-token
EOF
```

`./scripts/setup-dev.sh` creates this file with placeholder values only when it is
missing; it never overwrites an existing vault.

### 5. Configure your LLM provider (optional — for live `plan` / `computer-use`)

Edit `fixtures/sample-app/finalstrike.yaml` for the provider you use. Ollama is
only the **committed example**; OpenAI, OpenRouter, LiteLLM, etc. are supported
via `llm.base_url` and `llm.model`:

```yaml
llm:
  provider: openai_compat
  base_url: [REDACTED]
  model: gpt-4o
```

Deterministic cassette tests use the isolated tree at
`tests/fixtures/cassette-smoke-v1/` — **not** your edited `fixtures/sample-app/`
config — so `pytest -q` stays green while you point the sample app at a live API.

Optional `computer_use.llm` overrides the action/vision model; when omitted, the
planner `llm` block is used.

### 6. Run tests the intended way

**Activate the venv** (recommended):

```bash
source .venv/bin/activate
pytest -q
```

Some orchestrator tests spawn a bare `pytest` subprocess. If the venv is not
activated and `pytest` is not on your shell `PATH`, **3 tests** in
`tests/test_p3_runners.py` fail with `pytest: not found`. Using
`.venv/bin/pytest` without activation can cause the same failure.

### 6. Sanity check

```bash
source .venv/bin/activate
finalstrike --version
finalstrike doctor --repo fixtures/sample-app
pytest -q
```

Doctor should exit **0**. Warnings for stub modules, planned fixture work, or
skipped optional tools (live LLM, `ydotool`) are normal on a minimal dev machine.

## Troubleshooting

### `externally-managed-environment` when running `pip install`

You are using **system** pip. Create and use `.venv` (see step 2). Do not
`sudo pip install`.

### `.venv/bin/pip: cannot execute: required file not found`

The virtualenv is **broken** (often created on another machine or with a removed
Python). Fix:

```bash
rm -rf .venv
./scripts/setup-dev.sh
```

### `python3 -m venv .venv` fails

Install the venv module: `sudo apt install python3.12-venv` (adjust version).

### `pytest: not found` (3 failures in `test_p3_runners.py`)

```bash
source .venv/bin/activate
which pytest   # should show .../FinalStrike/.venv/bin/pytest
pytest -q
```

### Six failures in `test_p1_context.py` (secrets)

Ensure `fixtures/sample-app/.finalstrike/secrets.env` exists with an
`OPENAI_API_KEY` entry. The value may be your real API key.

### Optional: live LLM or computer-use on a GUI VM

Not required for default `pytest -q`. See `docs/PHASE_GAPS.md` and
`docs/P6_APPROACH.md` for Chrome/Chromium, `xdotool`, and vision-model setup.
