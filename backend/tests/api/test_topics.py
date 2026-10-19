from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.adapters.api.dependencies import get_topic_service
from app.main import app
from app.schemas import TopicCreate, TopicUpdate

client = TestClient(app)

mock_topic = {"id": 5, "section_id": 3, "name": "Machine learning"}
mock_topics = [
    {"id": 5, "section_id": 3, "name": "Machine learning"},
    {"id": 6, "section_id": 3, "name": "Databases"},
]


@pytest.fixture
def mock_topic_service():
    service = MagicMock()
    service.list_topics = AsyncMock(return_value=mock_topics)
    service.get_topic = AsyncMock(return_value=mock_topic)
    service.create_topic = AsyncMock(return_value=mock_topic)
    service.update_topic = AsyncMock(return_value={**mock_topic, "name": "Updated"})
    service.delete_topic = AsyncMock(return_value=None)
    return service


@pytest.fixture(autouse=True)
def override_dependencies(mock_topic_service):
    app.dependency_overrides[get_topic_service] = lambda: mock_topic_service
    yield
    app.dependency_overrides.clear()


# --- list ---


def test_list_topics_by_section(mock_topic_service):
    response = client.get("/api/v1/topics?sectionId=3")

    assert response.status_code == 200
    assert response.history == []
    assert [t["name"] for t in response.json()] == ["Machine learning", "Databases"]
    mock_topic_service.list_topics.assert_called_once_with(3)


def test_list_topics_without_section_uses_trailing_slash(mock_topic_service):
    response = client.get("/api/v1/topics/")

    assert response.status_code == 200
    assert response.history == []
    mock_topic_service.list_topics.assert_called_once_with(None)


def test_list_topics_rejects_non_positive_section():
    assert client.get("/api/v1/topics?sectionId=0").status_code == 422


# --- create ---


@pytest.mark.parametrize("path", ["/api/v1/topics/", "/api/v1/topics"])
def test_create_topic(mock_topic_service, path):
    response = client.post(f"{path}?sectionId=3", json={"name": "Machine learning"})

    assert response.status_code == 201
    assert response.history == []
    assert response.json()["id"] == 5
    mock_topic_service.create_topic.assert_called_once_with(3, TopicCreate(name="Machine learning"))


def test_create_topic_requires_section(mock_topic_service):
    response = client.post("/api/v1/topics/", json={"name": "Machine learning"})

    assert response.status_code == 422
    mock_topic_service.create_topic.assert_not_called()


@pytest.mark.parametrize("name", ["ab", "  ab  ", "x" * 51])
def test_create_topic_validates_name(mock_topic_service, name):
    response = client.post("/api/v1/topics/?sectionId=3", json={"name": name})

    assert response.status_code == 422
    mock_topic_service.create_topic.assert_not_called()


# --- single ---


def test_get_topic(mock_topic_service):
    response = client.get("/api/v1/topics/5")

    assert response.status_code == 200
    assert response.json() == mock_topic
    mock_topic_service.get_topic.assert_called_once_with(5)


def test_get_topic_not_found(mock_topic_service):
    mock_topic_service.get_topic.side_effect = HTTPException(404, "Тема не найдена")

    response = client.get("/api/v1/topics/404")

    assert response.status_code == 404
    assert response.json()["detail"] == "Тема не найдена"


def test_update_topic_takes_section_from_query(mock_topic_service):
    response = client.put("/api/v1/topics/5?sectionId=3", json={"name": "Updated"})

    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
    mock_topic_service.update_topic.assert_called_once_with(5, TopicUpdate(name="Updated", section_id=3))


def test_update_topic_body_section_wins_over_query(mock_topic_service):
    client.put("/api/v1/topics/5?sectionId=3", json={"name": "Updated", "section_id": 9})

    mock_topic_service.update_topic.assert_called_once_with(5, TopicUpdate(name="Updated", section_id=9))


def test_update_topic_without_section(mock_topic_service):
    client.put("/api/v1/topics/5", json={"name": "Updated"})

    mock_topic_service.update_topic.assert_called_once_with(5, TopicUpdate(name="Updated"))


def test_delete_topic(mock_topic_service):
    response = client.delete("/api/v1/topics/5")

    assert response.status_code == 204
    mock_topic_service.delete_topic.assert_called_once_with(5)


# --- openapi ---


def test_openapi_exposes_canonical_topic_paths():
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/v1/topics" in paths
    assert "/api/v1/topics/{topic_id}" in paths
    assert "/api/v1/topics/" not in paths
