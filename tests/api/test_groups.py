from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.adapters.api.dependencies import get_current_user, get_group_invite_service, get_group_service
from app.enums.group import GroupStatus
from app.main import app
from app.models import Group
from app.schemas import GroupUpdate, InviteTokenResponse

client = TestClient(app)

mock_user_id = 7
mock_group = Group(id=5, section_id=3, name="Alpha", status=GroupStatus.FORMING, member_count=1)


@pytest.fixture
def mock_group_service():
    service = MagicMock()
    service.update_group = AsyncMock(return_value=mock_group)
    return service


@pytest.fixture
def mock_invite_service():
    service = MagicMock()
    service.create_invite_token = AsyncMock(
        return_value=InviteTokenResponse(token="abc", expired_at=datetime(2026, 1, 1, tzinfo=UTC))
    )
    return service


@pytest.fixture(autouse=True)
def override_dependencies(mock_group_service, mock_invite_service):
    app.dependency_overrides[get_group_service] = lambda: mock_group_service
    app.dependency_overrides[get_group_invite_service] = lambda: mock_invite_service
    app.dependency_overrides[get_current_user] = lambda: mock_user_id
    yield
    app.dependency_overrides.clear()


def test_update_group_takes_id_from_path(mock_group_service):
    response = client.patch("/api/v1/groups/5", json={"name": "Beta"})

    assert response.status_code == 200
    assert response.json()["id"] == 5
    mock_group_service.update_group.assert_awaited_once_with(mock_user_id, 5, GroupUpdate(name="Beta"))


def test_update_group_not_found(mock_group_service):
    mock_group_service.update_group.return_value = "NOT_FOUND"

    assert client.patch("/api/v1/groups/5", json={"name": "Beta"}).status_code == 404


def test_update_group_not_leader(mock_group_service):
    mock_group_service.update_group.return_value = "NOT_LEADER"

    assert client.patch("/api/v1/groups/5", json={"name": "Beta"}).status_code == 403


def test_invite_token_takes_group_id_from_path(mock_invite_service):
    response = client.post("/api/v1/groups/5/invite-token")

    assert response.status_code == 200
    assert response.json()["token"] == "abc"
    mock_invite_service.create_invite_token.assert_awaited_once_with(group_id=5, person_id=mock_user_id)


def test_openapi_exposes_group_paths():
    paths = client.get("/openapi.json").json()["paths"]

    assert "patch" in paths["/api/v1/groups/{group_id}"]
    assert "/api/v1/groups/{group_id}/invite-token" in paths
    assert "/api/v1/groups/{group-id}/invite-token" not in paths
