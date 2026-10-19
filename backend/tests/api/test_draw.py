from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.adapters.api.dependencies import get_draw_service
from app.main import app
from app.schemas import DrawGroupRead, DrawResultRead, DrawRunResult, DrawTopicRead

client = TestClient(app)

mock_results = [
    DrawResultRead(group_id=1, group_name="Alpha", topics=[DrawTopicRead(topic_id=10, topic_name="Machine learning")]),
    DrawResultRead(group_id=2, group_name="Beta", topics=[]),
]
mock_run_result = DrawRunResult(
    section_id=3,
    results=mock_results,
    empty_groups=[DrawGroupRead(group_id=2, group_name="Beta")],
    total_topics=1,
    total_groups=2,
)


@pytest.fixture
def mock_draw_service():
    service = MagicMock()
    service.run_draw = AsyncMock(return_value=mock_run_result)
    service.get_results = AsyncMock(return_value=mock_results)
    return service


@pytest.fixture(autouse=True)
def override_dependencies(mock_draw_service):
    app.dependency_overrides[get_draw_service] = lambda: mock_draw_service
    yield
    app.dependency_overrides.clear()


def test_run_draw(mock_draw_service):
    response = client.post("/api/v1/draw/run?sectionId=3")

    assert response.status_code == 200
    body = response.json()
    assert body["section_id"] == 3
    assert body["total_groups"] == 2
    assert body["empty_groups"] == [{"group_id": 2, "group_name": "Beta"}]
    mock_draw_service.run_draw.assert_called_once_with(3)


def test_run_draw_requires_section(mock_draw_service):
    assert client.post("/api/v1/draw/run").status_code == 422
    mock_draw_service.run_draw.assert_not_called()


def test_run_draw_conflict(mock_draw_service):
    mock_draw_service.run_draw.side_effect = HTTPException(409, "Нет тем для распределения в секции")

    response = client.post("/api/v1/draw/run?sectionId=3")

    assert response.status_code == 409


def test_get_draw_results(mock_draw_service):
    response = client.get("/api/v1/draw-results?sectionId=3")

    assert response.status_code == 200
    assert response.json() == [
        {"group_id": 1, "group_name": "Alpha", "topics": [{"topic_id": 10, "topic_name": "Machine learning"}]},
        {"group_id": 2, "group_name": "Beta", "topics": []},
    ]
    mock_draw_service.get_results.assert_called_once_with(3)


def test_get_draw_results_requires_section():
    assert client.get("/api/v1/draw-results").status_code == 422


def test_openapi_exposes_draw_paths():
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/v1/draw/run" in paths
    assert "/api/v1/draw-results" in paths
