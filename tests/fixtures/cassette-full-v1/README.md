# Cassette full fixture (committed)

Frozen copy of `fixtures/sample-app` config used **only** by deterministic
planner cassette tests (`tests/llm_recordings/planner/full-v1/`).

Developers may customize `fixtures/sample-app/finalstrike.yaml` and
`.finalstrike/secrets.env` for live OpenAI/Ollama/etc. without breaking
`pytest -q`. When planner prompts or this snapshot change, refresh the cassette
and update these files together.
