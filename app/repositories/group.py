from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.group import GroupStatus
from app.models import Group, GroupParticipant, Participant
from app.schemas import GroupFilter, GroupUpdate


class GroupRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_groups(self, filters: GroupFilter) -> Sequence[Group]:
        stmt = select(Group)

        filter_dict = filters.model_dump(exclude_unset=True)

        for field, value in filter_dict.items():
            if hasattr(Group, field):
                column = getattr(Group, field)
                stmt = stmt.where(column.is_(None)) if value is None else stmt.where(column == value)

        stmt = stmt.order_by(Group.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_group_by_id(self, group_id: int) -> Group | None:
        stmt = select(Group).where(Group.id == group_id)

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_group(self, section_id: int, name: str) -> Group:
        group = Group(
            section_id=section_id,
            name=name,
            status=GroupStatus.FORMING,
            member_count=0,
        )

        self._session.add(group)

        await self._session.flush()
        await self._session.refresh(group)
        return group

    async def update_group(self, group: Group, data: GroupUpdate) -> Group:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(group, field, value)

        await self._session.flush()
        await self._session.refresh(group)
        return group

    async def delete_group(self, group: Group) -> None:
        await self._session.delete(group)
        await self._session.flush()

    async def update_status(self, group: Group, status: GroupStatus) -> Group:
        group.status = status

        await self._session.flush()
        await self._session.refresh(group)

        return group

    async def set_registration_time(self, group: Group) -> Group:
        group.registration_time = func.now()

        await self._session.flush()
        await self._session.refresh(group)

        return group

    async def increment_count(self, group: Group) -> Group:
        group.member_count += 1

        await self._session.flush()
        await self._session.refresh(group)

        return group

    async def is_leader(self, group_id: int, user_id: int) -> bool:
        stmt = (
            select(GroupParticipant)
            .where(GroupParticipant.group_id == group_id)
            .join(Participant, GroupParticipant.participant_id == Participant.id)
            .where(Participant.person_id == user_id)
            .where(Participant.is_group_leader)
        )

        result = await self._session.execute(stmt)
        return result.scalar() is not None
