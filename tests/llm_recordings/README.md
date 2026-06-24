# LLM recordings (cassettes)

Committed request/response fixtures for **deterministic integration tests**
without calling a live LLM in default CI.

## Layout

```
llm_recordings/
  planner/
    smoke-v1/
      meta.yaml              # hashes for invalidation
      messages.json          # exact planner prompt messages
      responses.json         # raw LLM output(s), one per attempt
      plan.canonical.json    # normalized VerificationPlan golden file
    full-v1/                 # acceptance-full.md (Tiers 1–5)
  computer_use/              # P6+: same shape per UI scenario
    smoke-title-v1/          # landing page title (port 8080)
    full-tasks-title-v1/     # tasks page title
```

## Default CI

Cassette replay tests run in the normal `pytest -q` suite — no live LLM required.

## Refresh a cassette (after prompt or acceptance changes)

When `assert_cassette_matches_context` fails, re-record from a machine with
the configured LLM endpoint reachable (`finalstrike.yaml` + secrets):

```bash
export FINALSTRIKE_RECORD_LLM=1
pytest -m requires_live_llm tests/test_p5_planner_live.py::test_record_smoke_planner_cassette -q
pytest -m requires_live_llm tests/test_p5_planner_live.py::test_record_full_planner_cassette -q
pytest tests/test_p5_planner_integration.py tests/test_p5_planner_full_integration.py -q
git add tests/llm_recordings/ tests/fixtures/cassette-full-v1/
```

## Live structural checks (optional)

```bash
pytest -m requires_live_llm tests/test_p5_planner_live.py -q
```

Live tests assert **structure** (acceptance + `capabilities.yaml` coverage),
not bitwise equality with the canonical plan.
