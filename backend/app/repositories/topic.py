from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Topic
from app.schemas import TopicCreate, TopicUpdate


class TopicRepository:
    """Data access layer for topics."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_topic_by_id(self, topic_id: int) -> Topic | None:
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_topics(self, section_id: int | None = None) -> Sequence[Topic]:
        """List topics, optionally restricted to one section."""
        stmt = select(Topic).order_by(Topic.id)
        if section_id is not None:
            stmt = stmt.where(Topic.section_id == section_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, section_id: int, data: TopicCreate) -> Topic:
        topic = Topic(section_id=section_id, name=data.name)
        self._session.add(topic)
        await self._session.flush()
        await self._session.refresh(topic)
        await self._session.commit()
        return topic

    async def update(self, topic: Topic, data: TopicUpdate) -> Topic:
        for key, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(topic, key, value)
        await self._session.flush()
        await self._session.refresh(topic)
        await self._session.commit()
        return topic

    async def delete(self, topic: Topic) -> None:
        await self._session.delete(topic)
        await self._session.flush()
        await self._session.commit()
