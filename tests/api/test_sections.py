from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.adapters.api.dependencies import get_section_service
from app.main import app

# Создаем тестовый клиент
client = TestClient(app)

# Мок-данные для тестирования
mock_section_data = {"id": 1, "name": "Test Section", "description": "Test Description"}

mock_section_list = [
    {"id": 1, "name": "Section 1", "description": "Desc 1"},
    {"id": 2, "name": "Section 2", "description": "Desc 2"},
]


@pytest.fixture
def mock_section_service():
    """Фикстура для мокирования SectionService"""
    service = MagicMock()

    # Мокаем все методы сервиса
    service.list_sections = AsyncMock(return_value=mock_section_list)
    service.get_section_by_id = AsyncMock(return_value=mock_section_data)
    service.create_section = AsyncMock(return_value=mock_section_data)
    service.update_section = AsyncMock(return_value={**mock_section_data, "name": "Updated Section"})
    service.delete_section = AsyncMock(return_value=None)

    return service


@pytest.fixture(autouse=True)
def override_dependencies(mock_section_service):
    """Переопределяем зависимости FastAPI для тестов"""
    app.dependency_overrides[get_section_service] = lambda: mock_section_service
    yield
    app.dependency_overrides.clear()


# Тест GET / - получение списка секций
def test_read_sections(mock_section_service):
    """Тест получения списка всех секций"""
    response = client.get("/api/v1/sections/?skip=0&limit=100")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Section 1"
    mock_section_service.list_sections.assert_called_once_with(0, 100)


# Тест GET /{section_id} - получение одной секции
def test_read_section(mock_section_service):
    """Тест получения секции по ID"""
    section_id = 1
    response = client.get(f"/api/v1/sections/{section_id}")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Test Section"
    mock_section_service.get_section_by_id.assert_called_once_with(section_id)


# Тест POST / - создание секции
def test_create_section(mock_section_service):
    """Тест создания новой секции"""
    new_section = {"name": "New Section", "description": "New Description"}

    response = client.post("/api/v1/sections/", json=new_section)

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Test Section"
    mock_section_service.create_section.assert_called_once()


# Тест PATCH /{section_id} - обновление секции
def test_update_section(mock_section_service):
    """Тест обновления существующей секции"""
    section_id = 1
    update_data = {"name": "Updated Section"}

    response = client.patch(f"/api/v1/sections/{section_id}", json=update_data)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Section"
    mock_section_service.update_section.assert_called_once()


# Тест DELETE /{section_id} - удаление секции
def test_delete_section(mock_section_service):
    """Тест удаления секции"""
    section_id = 1
    response = client.delete(f"/api/v1/sections/{section_id}")

    assert response.status_code == 204
    mock_section_service.delete_section.assert_called_once_with(section_id)


# Дополнительные тесты для edge cases
def test_read_sections_with_pagination(mock_section_service):
    """Тест пагинации списка секций"""
    response = client.get("/api/v1/sections/?skip=10&limit=5")

    assert response.status_code == 200
    mock_section_service.list_sections.assert_called_once_with(10, 5)


def test_read_section_not_found(mock_section_service):
    """Тест получения несуществующей секции"""
    from fastapi import HTTPException

    mock_section_service.get_section_by_id = AsyncMock(side_effect=HTTPException(status_code=404, detail="Not found"))

    response = client.get("/api/v1/sections/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not found"
    mock_section_service.get_section_by_id.assert_called_once_with(999)
