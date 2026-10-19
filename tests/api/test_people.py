from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.adapters.api.dependencies import get_current_user, get_person_service
from app.main import app

client = TestClient(app)

mock_person_update_full = {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "title": "Mr.",
    "position": "Senior Engineer",
}

mock_myself_update = {
    "position": "Lead Engineer",
}

mock_person_read = {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "middle_name": None,
    "email": "john@example.com",
    "title": "Mr.",
    "degree": "PhD",
    "position": "Engineer",
    "workplace": "Company Inc.",
    "tg_name": "@johndoe",
}


@pytest.fixture
def mock_person_service():
    service = MagicMock()
    service.get_person_by_id = AsyncMock(return_value=mock_person_read)
    service.put_person = AsyncMock(return_value=mock_person_read)
    service.update_person = AsyncMock(return_value=mock_person_read)
    service.create_person = AsyncMock(return_value=mock_person_read)
    return service


@pytest.fixture
def mock_user_id():
    return 1


@pytest.fixture(autouse=True)
def override_dependencies(mock_person_service, mock_user_id):
    app.dependency_overrides[get_person_service] = lambda: mock_person_service
    app.dependency_overrides[get_current_user] = lambda: mock_user_id
    yield
    app.dependency_overrides.clear()


# ---------- PUT /api/v1/person ----------
def test_put_person_success(mock_person_service):
    response = client.put("/api/v1/person/", json=mock_person_update_full)
    assert response.status_code == 200
    assert response.json()["id"] == 1

    call_args = mock_person_service.put_person.call_args
    assert call_args is not None
    arg = call_args[0][0]
    assert arg.id == 1
    assert arg.email == "john@example.com"


def test_put_person_unauthorized(mock_person_service):
    async def raise_401():
        raise HTTPException(status_code=401, detail="missing token")

    app.dependency_overrides[get_current_user] = raise_401
    response = client.put("/api/v1/person/", json=mock_person_update_full)
    assert response.status_code == 401
    mock_person_service.put_person.assert_not_called()
    app.dependency_overrides[get_current_user] = lambda: 1


# ---------- POST /api/v1/person ----------
def test_create_person_success(mock_person_service):
    response = client.post("/api/v1/person/", json=mock_person_update_full)
    assert response.status_code == 200
    assert response.json()["id"] == 1

    call_args = mock_person_service.create_person.call_args
    assert call_args is not None
    arg = call_args[0][0]
    assert arg.id == 1
    assert arg.first_name == "John"


def test_create_person_conflict(mock_person_service):
    mock_person_service.create_person = AsyncMock(
        side_effect=HTTPException(status_code=409, detail="Person with id 1 doesn't exist")
    )
    response = client.post("/api/v1/person/", json=mock_person_update_full)
    assert response.status_code == 409
    assert "doesn't exist" in response.json()["detail"]


# ---------- PATCH /api/v1/person ----------
def test_update_person_success(mock_person_service):
    response = client.patch("/api/v1/person/", json=mock_myself_update)
    assert response.status_code == 200
    assert response.json()["id"] == 1

    call_args = mock_person_service.update_person.call_args
    assert call_args is not None
    arg = call_args[0][0]
    assert arg.id == 1
    assert arg.position == "Lead Engineer"


def test_update_person_not_found(mock_person_service):
    mock_person_service.update_person = AsyncMock(
        side_effect=HTTPException(status_code=409, detail="Person with id 1 doesn't exist")
    )
    response = client.patch("/api/v1/person/", json={"first_name": "Jane"})
    assert response.status_code == 409


# ---------- GET /api/v1/person (by query param) ----------
def test_get_person_by_id_success(mock_person_service):
    response = client.get("/api/v1/person/?person_id=1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_person_service.get_person_by_id.assert_called_once_with(1)


def test_get_person_by_id_not_found(mock_person_service):
    mock_person_service.get_person_by_id = AsyncMock(
        side_effect=HTTPException(status_code=404, detail="Person with id 999 not found")
    )
    response = client.get("/api/v1/person/?person_id=999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# ---------- GET /api/v1/person/me ----------
def test_get_me_success(mock_person_service, mock_user_id):
    response = client.get("/api/v1/person/me")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_person_service.get_person_by_id.assert_called_once_with(mock_user_id)


def test_get_me_not_found(mock_person_service):
    mock_person_service.get_person_by_id = AsyncMock(
        side_effect=HTTPException(status_code=404, detail="Person not found")
    )
    response = client.get("/api/v1/person/me")
    assert response.status_code == 404


def test_get_me_unauthorized():
    async def raise_401():
        raise HTTPException(status_code=401, detail="missing token")

    app.dependency_overrides[get_current_user] = raise_401
    response = client.get("/api/v1/person/me")
    assert response.status_code == 401
    app.dependency_overrides[get_current_user] = lambda: 1
