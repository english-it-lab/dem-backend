from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.adapters.api.dependencies import get_score_history_service
from app.main import app
from app.schemas import ScoreHistoryCreate, ScoreHistoryUpdate

client = TestClient(app)

mock_score_history_data = {"id": 1, "jury_scores_id": 10, "jury_id": 2, "update_time": None}
mock_score_history_list = [
    {"id": 1, "jury_scores_id": 10, "jury_id": 2, "update_time": None},
    {"id": 2, "jury_scores_id": 10, "jury_id": 3, "update_time": None},
]


@pytest.fixture
def mock_score_history_service():
    service = MagicMock()
    service.list_history = AsyncMock(return_value=mock_score_history_list)
    service.get_history_by_id = AsyncMock(return_value=mock_score_history_data)
    service.create_history = AsyncMock(return_value=mock_score_history_data)
    service.update_history = AsyncMock(return_value={**mock_score_history_data, "jury_id": 3})
    service.delete_history = AsyncMock(return_value=True)
    return service


@pytest.fixture(autouse=True)
def override_score_history_dependencies(mock_score_history_service):
    app.dependency_overrides[get_score_history_service] = lambda: mock_score_history_service
    yield
    app.dependency_overrides.clear()


def test_list_score_history(mock_score_history_service):
    response = client.get("/api/v1/score-history/?jury_scores_id=10&jury_id=2")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["jury_scores_id"] == 10
    mock_score_history_service.list_history.assert_called_once_with(jury_scores_id=10, jury_id=2)


def test_get_score_history(mock_score_history_service):
    response = client.get("/api/v1/score-history/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_score_history_service.get_history_by_id.assert_called_once_with(1)


def test_create_score_history(mock_score_history_service):
    payload = {"jury_scores_id": 10, "jury_id": 2}

    response = client.post("/api/v1/score-history/", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == 1
    mock_score_history_service.create_history.assert_called_once_with(ScoreHistoryCreate(**payload))


def test_update_score_history(mock_score_history_service):
    payload = {"jury_id": 3}

    response = client.patch("/api/v1/score-history/1", json=payload)

    assert response.status_code == 200
    assert response.json()["jury_id"] == 3
    mock_score_history_service.update_history.assert_called_once_with(1, ScoreHistoryUpdate(**payload))


def test_delete_score_history(mock_score_history_service):
    response = client.delete("/api/v1/score-history/1")

    assert response.status_code == 204
    mock_score_history_service.delete_history.assert_called_once_with(1)


def test_get_score_history_not_found(mock_score_history_service):
    mock_score_history_service.get_history_by_id = AsyncMock(return_value=None)

    response = client.get("/api/v1/score-history/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Score history entry with id 999 not found"
