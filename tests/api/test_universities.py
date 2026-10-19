from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.adapters.api.dependencies import get_university_service
from app.main import app
from app.schemas import UniversityCreate

client = TestClient(app)


mock_university_data = {"id": 1, "name": "Test University", "description": "Test Description"}

mock_university_list = [
    {"id": 1, "name": "University 1", "description": "Desc 1"},
    {"id": 2, "name": "University 2", "description": "Desc 2"},
]


@pytest.fixture
def mock_university_service():
    """Фикстура для мокирования UniversityService"""
    service = MagicMock()

    # Мокаем методы сервиса
    service.list_universities = AsyncMock(return_value=mock_university_list)
    service.create_university = AsyncMock(return_value=mock_university_data)

    return service


@pytest.fixture(autouse=True)
def override_university_dependencies(mock_university_service):
    """Переопределяем зависимости FastAPI для тестов университетов"""
    app.dependency_overrides[get_university_service] = lambda: mock_university_service
    yield
    app.dependency_overrides.clear()


# Тест GET / - получение списка университетов
def test_list_universities(mock_university_service):
    """Тест получения списка всех университетов"""
    response = client.get("/api/v1/universities/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "University 1"
    mock_university_service.list_universities.assert_called_once()


# Тест POST / - создание университета
def test_create_university(mock_university_service):
    """Тест создания нового университета"""
    new_university = {"name": "New University", "description": "New Description"}

    response = client.post("/api/v1/universities/", json=new_university)

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Test University"
    # Fix: Create the expected Pydantic model instance for comparison
    expected_model = UniversityCreate(name="New University")
    mock_university_service.create_university.assert_called_once_with(expected_model)


# Дополнительные тесты для edge cases
def test_create_university_invalid_data():
    """Тест создания университета с невалидными данными"""
    invalid_data = {"invalid_field": "value"}  # Отсутствует обязательное поле name

    response = client.post("/api/v1/universities/", json=invalid_data)

    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]


def test_list_universities_empty(mock_university_service):
    """Тест получения пустого списка университетов"""
    mock_university_service.list_universities = AsyncMock(return_value=[])

    response = client.get("/api/v1/universities/")

    assert response.status_code == 200
    assert len(response.json()) == 0
    mock_university_service.list_universities.assert_called_once()
