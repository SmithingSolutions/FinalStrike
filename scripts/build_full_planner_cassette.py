#!/usr/bin/env python3
"""Build planner/full-v1 cassette files (run from repo root)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from finalstrike.config.models import VerificationPlan
from finalstrike.fixture_capabilities import load_capabilities
from finalstrike.planner.prompt import build_planner_messages, planner_prompt_version
from tests.support.cassette_repo import (
    CASSETTE_ACCEPTANCE_FULL,
    CASSETTE_FULL_REPO,
    load_cassette_full_context,
)
from tests.support.llm_cassette import (
    messages_sha256,
    serialize_messages,
    sha256_file,
)
from tests.support.plan_assertions import (
    assert_plan_covers_acceptance,
    assert_plan_covers_capabilities,
    assert_plan_has_layer_coverage,
)

CASSETTE_ID = "full-v1"
CASSETTE_DIR = ROOT / "tests" / "llm_recordings" / "planner" / CASSETTE_ID

PLAN = {
    "gaps": [],
    "scenarios": [
        {
            "id": "ac-1",
            "source": "API health endpoint returns 200 on GET /health",
            "layers": {
                "terminal": [],
                "api": [
                    {
                        "method": "GET",
                        "path": "/health",
                        "expect": {"status": 200},
                    }
                ],
                "ui": [],
            },
        },
        {
            "id": "ac-2",
            "source": "API returns 200 on GET /api/tasks with a JSON array of tasks",
            "layers": {
                "terminal": [],
                "api": [
                    {
                        "method": "GET",
                        "path": "/api/tasks",
                        "expect": {"status": 200},
                    }
                ],
                "ui": [],
            },
        },
        {
            "id": "ac-3",
            "source": 'API returns 201 on POST /api/tasks with JSON body {"title": "<title>", "description": "<optional>"}',
            "layers": {
                "terminal": [],
                "api": [
                    {
                        "method": "POST",
                        "path": "/api/tasks",
                        "expect": {"status": 201},
                        "body": {"title": "Cassette task", "description": "from planner"},
                    }
                ],
                "ui": [],
            },
        },
        {
            "id": "ac-4",
            "source": "API returns 200 on PATCH /api/tasks/{id} with JSON body {\"completed\": true} or {\"completed\": false}",
            "layers": {
                "terminal": [],
                "api": [
                    {
                        "method": "PATCH",
                        "path": "/api/tasks/{id}",
                        "expect": {"status": 200},
                        "body": {"completed": True},
                    }
                ],
                "ui": [],
            },
        },
        {
            "id": "ac-5",
            "source": "API returns 204 on DELETE /api/tasks/{id}",
            "layers": {
                "terminal": [],
                "api": [
                    {
                        "method": "DELETE",
                        "path": "/api/tasks/{id}",
                        "expect": {"status": 204},
                    }
                ],
                "ui": [],
            },
        },
        {
            "id": "ac-6",
            "source": "API returns 200 on GET /api/tasks/{id} with the matching task JSON",
            "layers": {
                "terminal": [],
                "api": [
                    {
                        "method": "GET",
                        "path": "/api/tasks/{id}",
                        "expect": {"status": 200},
                    }
                ],
                "ui": [],
            },
        },
        {
            "id": "ac-7",
            "source": 'Tasks page loads at http://localhost:8080/tasks/ with page title "Sample App - Tasks"',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'Open http://localhost:8080/tasks/ and verify the page title is "Sample App - Tasks"'
                    }
                ],
            },
        },
        {
            "id": "ac-8",
            "source": "User can open the Tasks page and see the task list",
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": "Open http://localhost:8080/tasks/ and verify the task list is visible"
                    }
                ],
            },
        },
        {
            "id": "ac-9",
            "source": 'User can click "New Task", fill title and description, and save',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'On http://localhost:8080/tasks/, click "New Task", fill title and description, save the form'
                    }
                ],
            },
        },
        {
            "id": "ac-10",
            "source": "New task appears in the list with correct title",
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": "After creating a task, verify its title appears in the task list on the Tasks page"
                    }
                ],
            },
        },
        {
            "id": "ac-11",
            "source": 'User can click "Mark Done" on a task and see a Done badge with strikethrough title',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'On the Tasks page, click "Mark Done" on a task and verify a Done badge with strikethrough title'
                    }
                ],
            },
        },
        {
            "id": "ac-12",
            "source": 'User can click "Mark Active" to clear the done state',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'On the Tasks page, click "Mark Active" on a completed task and verify the done state clears'
                    }
                ],
            },
        },
        {
            "id": "ac-13",
            "source": 'User can click "Delete", confirm with "Confirm Delete" in the modal, and the task is removed from the list',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'Delete a task using "Delete", confirm with "Confirm Delete", and verify it is removed from the list'
                    }
                ],
            },
        },
        {
            "id": "ac-14",
            "source": 'User can click "Cancel" or press Escape to dismiss the delete modal without deleting',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'Open the delete modal, click "Cancel" or press Escape, and verify the task remains in the list'
                    }
                ],
            },
        },
        {
            "id": "ac-15",
            "source": 'User can click "Load Demo Tasks" to seed 15 tasks and scroll the task list',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'Click "Load Demo Tasks", verify 15 tasks appear, and scroll the task list'
                    }
                ],
            },
        },
        {
            "id": "ac-16",
            "source": 'Settings page loads at http://localhost:8080/settings/ with page title "Sample App - Settings"',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'Open http://localhost:8080/settings/ and verify the page title is "Sample App - Settings"'
                    }
                ],
            },
        },
        {
            "id": "ac-17",
            "source": 'User can choose Light or Dark theme and click "Save Settings" to see "Settings saved."',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'On Settings, choose Light or Dark theme, click "Save Settings", and verify "Settings saved." appears'
                    }
                ],
            },
        },
        {
            "id": "ac-18",
            "source": "User can choose a default sort order (Newest first, Oldest first, Title A-Z) on Settings",
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": "On Settings, choose a default sort order (Newest first, Oldest first, or Title A-Z) and save"
                    }
                ],
            },
        },
        {
            "id": "ac-19",
            "source": "Tasks page search box filters the visible list as the user types",
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": "On the Tasks page, type in the search box and verify the visible task list filters as you type"
                    }
                ],
            },
        },
        {
            "id": "ac-20",
            "source": 'User can click "Import Tasks", paste titles (one per line), click Next, review preview, and Confirm Import',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'Use the Import Tasks wizard: paste titles, click Next, review preview, and Confirm Import'
                    }
                ],
            },
        },
        {
            "id": "ac-21",
            "source": "Imported tasks appear in the task list via POST /api/tasks",
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": "After confirming import in the wizard, verify imported tasks appear in the task list"
                    }
                ],
            },
        },
        {
            "id": "ac-22",
            "source": "User can click a task title on the Tasks page to open http://localhost:8080/tasks/{id}",
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": "On the Tasks page, click a task title and verify the browser opens the task detail URL /tasks/{id}"
                    }
                ],
            },
        },
        {
            "id": "ac-23",
            "source": 'Task detail page shows page title "Sample App - Task Detail" with full title and description',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'Open a task detail page and verify title "Sample App - Task Detail" with full title and description'
                    }
                ],
            },
        },
        {
            "id": "ac-24",
            "source": "Home page at http://localhost:8080/ shows a Task overview with total, active, and done counts",
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": "Open http://localhost:8080/ and verify the Task overview dashboard shows total, active, and done counts"
                    }
                ],
            },
        },
        {
            "id": "ac-25",
            "source": "Recent tasks on the home page link to task detail pages",
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": "On the home page, verify recent task links navigate to task detail pages"
                    }
                ],
            },
        },
        {
            "id": "ac-26",
            "source": "Dashboard counts match GET /api/tasks results",
            "layers": {
                "terminal": [],
                "api": [
                    {
                        "method": "GET",
                        "path": "/api/tasks",
                        "expect": {"status": 200},
                    }
                ],
                "ui": [
                    {
                        "instruction": "Compare home dashboard total, active, and done counts against the task list from GET /api/tasks"
                    }
                ],
            },
        },
        {
            "id": "ac-27",
            "source": 'Frontend landing page loads at / with title "Sample App"',
            "layers": {
                "terminal": [],
                "api": [],
                "ui": [
                    {
                        "instruction": 'Open http://localhost:8080/ and verify the page title is "Sample App"'
                    }
                ],
            },
        },
        {
            "id": "ac-28",
            "source": "Unit tests pass via `pytest -q`",
            "layers": {
                "terminal": [
                    {
                        "command": "pytest -q",
                        "reason": "Run unit tests from finalstrike.yaml",
                    }
                ],
                "api": [],
                "ui": [],
            },
        },
    ],
}


def main() -> None:
    plan = VerificationPlan.model_validate(PLAN)
    acceptance_text = CASSETTE_ACCEPTANCE_FULL.read_text(encoding="utf-8")
    capabilities = load_capabilities(CASSETTE_FULL_REPO / "capabilities.yaml")

    assert_plan_has_layer_coverage(plan)
    assert_plan_covers_acceptance(plan, acceptance_text)
    assert_plan_covers_capabilities(plan, capabilities)

    context = load_cassette_full_context(inject_secrets=False)
    messages = serialize_messages(build_planner_messages(context))
    canonical = plan.model_dump(mode="json")
    raw_response = json.dumps(canonical, ensure_ascii=False)

    CASSETTE_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": CASSETTE_ID,
        "phase": 5,
        "component": "planner",
        "acceptance": str(
            CASSETTE_ACCEPTANCE_FULL.relative_to(ROOT)
        ),
        "acceptance_sha256": sha256_file(CASSETTE_ACCEPTANCE_FULL),
        "prompt_version": planner_prompt_version(),
        "messages_sha256": messages_sha256(messages),
        "recorded_with": {
            "base_url": context.config.llm.base_url,
            "model": context.config.llm.model,
            "temperature": 0.2,
            "source": "hand-authored canonical plan for deterministic CI replay",
        },
        "attempts": 1,
        "notes": "Refresh with FINALSTRIKE_RECORD_LLM=1 when prompt or acceptance changes.",
    }

    (CASSETTE_DIR / "meta.yaml").write_text(
        yaml.safe_dump(meta, sort_keys=False),
        encoding="utf-8",
    )
    (CASSETTE_DIR / "messages.json").write_text(
        json.dumps(messages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (CASSETTE_DIR / "responses.json").write_text(
        json.dumps([raw_response], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (CASSETTE_DIR / "plan.canonical.json").write_text(
        json.dumps(canonical, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote planner cassette to {CASSETTE_DIR}")


if __name__ == "__main__":
    main()
