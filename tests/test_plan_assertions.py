"""Unit tests for VerificationPlan structural assertions."""

from __future__ import annotations

from finalstrike.config.models import (
    APIExpectation,
    APIPlanStep,
    Scenario,
    ScenarioLayers,
    UIPlanStep,
    VerificationPlan,
)
from finalstrike.fixture_capabilities import (
    APICapability,
    CapabilityLayers,
    FixtureCapabilities,
    UICapability,
)
from tests.support.plan_assertions import (
    _api_paths_match,
    _ui_route_matches_instruction,
    assert_plan_covers_capabilities,
)


def test_api_paths_match_template_segment() -> None:
    assert _api_paths_match("/api/tasks/{id}", "/api/tasks/1")
    assert not _api_paths_match("/api/tasks/{id}", "/api/tasks")


def test_ui_route_matches_instruction_with_concrete_id() -> None:
    assert _ui_route_matches_instruction(
        "/tasks/{id}",
        "Open http://localhost:8080/tasks/42 and verify task detail",
    )


def test_live_api_substitute_accepts_ui_detail_coverage() -> None:
    plan = VerificationPlan(
        scenarios=[
            Scenario(
                id="ac-detail",
                source="Task detail page",
                layers=ScenarioLayers(
                    ui=[
                        UIPlanStep(
                            instruction=(
                                'Open http://localhost:8080/tasks/1 and verify '
                                'page title "Sample App - Task Detail"'
                            )
                        )
                    ],
                ),
            ),
        ],
    )
    capabilities = FixtureCapabilities(
        version="1",
        implemented=CapabilityLayers(
            api=[
                APICapability(
                    method="GET",
                    path="/api/tasks/{id}",
                    expect_status=200,
                ),
            ],
            ui=[
                UICapability(
                    route="/tasks/{id}",
                    title="Sample App - Task Detail",
                ),
            ],
            terminal=[],
        ),
        planned=CapabilityLayers(),
    )

    assert_plan_covers_capabilities(
        plan,
        capabilities,
        allow_ui_api_substitute=True,
    )


def test_strict_capabilities_require_api_step() -> None:
    plan = VerificationPlan(
        scenarios=[
            Scenario(
                id="ac-detail",
                source="Task detail page",
                layers=ScenarioLayers(
                    ui=[
                        UIPlanStep(
                            instruction="Open http://localhost:8080/tasks/1",
                        )
                    ],
                ),
            ),
        ],
    )
    capabilities = FixtureCapabilities(
        version="1",
        implemented=CapabilityLayers(
            api=[
                APICapability(
                    method="GET",
                    path="/api/tasks/{id}",
                    expect_status=200,
                ),
            ],
            ui=[],
            terminal=[],
        ),
        planned=CapabilityLayers(),
    )

    try:
        assert_plan_covers_capabilities(plan, capabilities)
    except AssertionError as exc:
        assert "GET /api/tasks/{id}" in str(exc)
    else:
        raise AssertionError("expected strict capability check to fail")
