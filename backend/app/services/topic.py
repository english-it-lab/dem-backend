from collections.abc import Sequence

from fastapi import HTTPException, status

from app.models import Topic
from app.repositories.topic import TopicRepository
from app.schemas import TopicCreate, TopicUpdate


class TopicService:
    """Business logic for section topics."""

    def __init__(self, topic_repo: TopicRepository) -> None:
        self._topic_repo = topic_repo

    async def list_topics(self, section_id: int | None = None) -> Sequence[Topic]:
        return await self._topic_repo.list_topics(section_id)

    async def get_topic(self, topic_id: int) -> Topic:
        topic = await self._topic_repo.get_topic_by_id(topic_id)
        if topic is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Тема не найдена")
        return topic

    async def create_topic(self, section_id: int, payload: TopicCreate) -> Topic:
        return await self._topic_repo.create(section_id, payload)

    async def update_topic(self, topic_id: int, payload: TopicUpdate) -> Topic:
        topic = await self.get_topic(topic_id)
        return await self._topic_repo.update(topic, payload)

    async def delete_topic(self, topic_id: int) -> None:
        topic = await self.get_topic(topic_id)
        await self._topic_repo.delete(topic)
