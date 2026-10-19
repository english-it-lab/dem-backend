import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.schemas import TopicCreate
from app.services.topic import TopicService


def make_service(section_exists=True):
    topic_repo = MagicMock()
    topic_repo.create = AsyncMock(return_value=SimpleNamespace(id=5, section_id=3, name="Machine learning"))
    section_repo = MagicMock()
    section_repo.get_section_by_id = AsyncMock(return_value=SimpleNamespace(id=3) if section_exists else None)
    return TopicService(topic_repo, section_repo), topic_repo, section_repo


def test_create_topic_checks_section_and_creates():
    service, topic_repo, section_repo = make_service()
    payload = TopicCreate(name="Machine learning")

    topic = asyncio.run(service.create_topic(3, payload))

    section_repo.get_section_by_id.assert_awaited_once_with(3)
    topic_repo.create.assert_awaited_once_with(3, payload)
    assert topic.id == 5


def test_create_topic_unknown_section_returns_404():
    service, topic_repo, _ = make_service(section_exists=False)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.create_topic(3, TopicCreate(name="Machine learning")))

    assert exc_info.value.status_code == 404
    topic_repo.create.assert_not_awaited()
