"""P5 planner integration tests for acceptance-full cassette replay."""

from __future__ import annotations

import json

import pytest

from finalstrike.config.models import VerificationPlan
from finalstrike.fixture_capabilities import load_capabilities
from finalstrike.planner.planner import generate_verification_plan
from finalstrike.planner.prompt import build_planner_messages
from tests.support.cassette_repo import (
    CASSETTE_ACCEPTANCE_FULL,
    CASSETTE_FULL_REPO,
    load_cassette_full_context,
)
from tests.support.llm_cassette import (
    ReplayCassetteProvider,
    assert_cassette_matches_context,
    load_planner_cassette,
    messages_sha256,
    serialize_messages,
)
from tests.support.plan_assertions import (
    assert_plan_covers_acceptance,
    assert_plan_covers_capabilities,
    assert_plan_has_layer_coverage,
)

FULL_CASSETTE_ID = "full-v1"


@pytest.fixture
def full_repo_context():
    return load_cassette_full_context(inject_secrets=False)


@pytest.fixture
def full_planner_cassette():
    return load_planner_cassette(FULL_CASSETTE_ID)


@pytest.mark.llm_cassette
def test_full_planner_cassette_meta_is_current(full_planner_cassette) -> None:
    cassette = full_planner_cassette
    assert cassette.meta.id == FULL_CASSETTE_ID
    assert cassette.meta.phase == 5
    assert cassette.meta.component == "planner"


@pytest.mark.llm_cassette
def test_full_planner_messages_stable_across_repo_absolute_path(
    full_planner_cassette,
) -> None:
    ctx_a = load_cassette_full_context(inject_secrets=False)
    other_root = CASSETTE_FULL_REPO.parent / "cassette-full-v1-mirror"
    ctx_b = ctx_a.model_copy(update={"repo": other_root})
    msgs_a = serialize_messages(build_planner_messages(ctx_a))
    msgs_b = serialize_messages(build_planner_messages(ctx_b))
    assert messages_sha256(msgs_a) == messages_sha256(msgs_b)


@pytest.mark.llm_cassette
def test_full_planner_cassette_matches_repo_inputs(
    full_repo_context,
    full_planner_cassette,
) -> None:
    assert_cassette_matches_context(
        full_planner_cassette,
        full_repo_context,
        acceptance_path=CASSETTE_ACCEPTANCE_FULL,
    )


@pytest.mark.llm_cassette
def test_full_planner_cassette_replay_matches_canonical(
    full_repo_context,
    full_planner_cassette,
) -> None:
    provider = ReplayCassetteProvider(full_planner_cassette.responses)
    plan = generate_verification_plan(full_repo_context, provider=provider)
    canonical = VerificationPlan.model_validate(full_planner_cassette.canonical_plan)
    assert plan == canonical
    assert provider.calls == 1


@pytest.mark.llm_cassette
def test_full_planner_cassette_replay_structural_coverage(
    full_repo_context,
    full_planner_cassette,
) -> None:
    provider = ReplayCassetteProvider(full_planner_cassette.responses)
    plan = generate_verification_plan(full_repo_context, provider=provider)
    capabilities = load_capabilities(CASSETTE_FULL_REPO / "capabilities.yaml")
    acceptance_text = CASSETTE_ACCEPTANCE_FULL.read_text(encoding="utf-8")

    assert_plan_has_layer_coverage(plan)
    assert_plan_covers_acceptance(plan, acceptance_text)
    assert_plan_covers_capabilities(plan, capabilities)


@pytest.mark.llm_cassette
def test_full_canonical_plan_json_is_stable(full_planner_cassette) -> None:
    on_disk = json.loads(
        (full_planner_cassette.root / "plan.canonical.json").read_text(
            encoding="utf-8"
        )
    )
    assert on_disk == full_planner_cassette.canonical_plan
