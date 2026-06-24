"""Tests for sample_app.server HTTP endpoints."""

from __future__ import annotations

import json
import socket
import threading
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from sample_app.server import HealthHandler, reset_tasks_for_testing


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def api_server():
    reset_tasks_for_testing()
    port = _free_port()
    server = HTTPServer(("127.0.0.1", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    try:
        yield base_url
    finally:
        server.shutdown()
        thread.join(timeout=2)


def _get(url: str) -> tuple[int, bytes]:
    with urlopen(url) as response:
        return response.status, response.read()


def _post_json(url: str, payload: dict) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        data = json.loads(raw) if raw else {}
        return exc.code, data


def _options(url: str) -> tuple[int, dict[str, str]]:
    request = Request(url, method="OPTIONS")
    with urlopen(request) as response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        return response.status, headers


def test_health_endpoint(api_server: str) -> None:
    status, body = _get(f"{api_server}/health")
    assert status == 200
    assert body == b"ok"


def test_serves_landing_page(api_server: str) -> None:
    status, body = _get(f"{api_server}/")
    assert status == 200
    assert b"Sample App" in body


def test_serves_tasks_page(api_server: str) -> None:
    status, body = _get(f"{api_server}/tasks/")
    assert status == 200
    assert b"Sample App - Tasks" in body
    assert b"New Task" in body


def test_tasks_path_redirects_to_trailing_slash(api_server: str) -> None:
    request = Request(f"{api_server}/tasks", method="GET")
    with urlopen(request) as response:
        assert response.status == 200
        assert response.url.endswith("/tasks/")


def test_post_task_success(api_server: str) -> None:
    status, task = _post_json(
        f"{api_server}/api/tasks",
        {"title": "Buy milk", "description": "2% organic"},
    )
    assert status == 201
    assert task["title"] == "Buy milk"
    assert task["description"] == "2% organic"
    assert task["id"] == 1
    assert task["completed"] is False


def test_post_without_title_fails(api_server: str) -> None:
    status, body = _post_json(f"{api_server}/api/tasks", {"description": "no title"})
    assert status == 400
    assert "title" in body["error"].lower()


def test_get_tasks_lists_created_tasks(api_server: str) -> None:
    _post_json(f"{api_server}/api/tasks", {"title": "First task"})
    _post_json(f"{api_server}/api/tasks", {"title": "Second task"})

    status, raw = _get(f"{api_server}/api/tasks")
    tasks = json.loads(raw.decode("utf-8"))
    assert status == 200
    assert len(tasks) == 2
    assert [task["title"] for task in tasks] == ["First task", "Second task"]


def test_cors_preflight_allows_post(api_server: str) -> None:
    status, headers = _options(f"{api_server}/api/tasks")
    assert status == 204
    assert headers.get("access-control-allow-origin") == "*"
    assert "POST" in headers.get("access-control-allow-methods", "")

    post_status, task = _post_json(
        f"{api_server}/api/tasks",
        {"title": "CORS task", "description": "via preflight"},
    )
    assert post_status == 201
    assert task["title"] == "CORS task"
