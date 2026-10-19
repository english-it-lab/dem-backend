from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Group, GroupTopic


class GroupTopicRepository:
    """Repository for GroupTopic entity (draw results)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, group_id: int, topic_id: int) -> GroupTopic:
        """Save draw result for a group."""
        group_topic = GroupTopic(group_id=group_id, topic_id=topic_id)
        self._session.add(group_topic)
        await self._session.commit()
        await self._session.refresh(group_topic)
        return group_topic

    async def clear_section(self, section_id: int) -> None:
        """Remove all draw results for a section."""
        # Delete group_topics where group belongs to the section
        stmt = delete(GroupTopic).where(
            GroupTopic.group_id.in_(select(Group.id).where(Group.section_id == section_id))
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def get_by_section(self, section_id: int) -> list[GroupTopic]:
        """Get all draw results for a section."""

        stmt = (
            select(GroupTopic)
            .join(Group)
            .where(Group.section_id == section_id)
            .options(selectinload(GroupTopic.group), selectinload(GroupTopic.topic))
            .order_by(GroupTopic.group_id, GroupTopic.id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
