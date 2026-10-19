from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import CommitteeMember
from app.schemas import CommitteeMemberCreate


class CommitteeMemberRepository:
    """Data access layer for committee members."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_event(self, event_id: int) -> Sequence[CommitteeMember]:
        stmt = (
            select(CommitteeMember)
            .where(CommitteeMember.event_id == event_id)
            .options(selectinload(CommitteeMember.person))
            .order_by(CommitteeMember.committee_type, CommitteeMember.sort_order)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, member_id: int) -> CommitteeMember | None:
        stmt = (
            select(CommitteeMember)
            .where(CommitteeMember.id == member_id)
            .options(selectinload(CommitteeMember.person))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: CommitteeMemberCreate) -> CommitteeMember:
        member = CommitteeMember(
            event_id=data.event_id,
            person_id=data.person_id,
            role=data.role,
            committee_type=data.committee_type,
            sort_order=data.sort_order,
        )
        self._session.add(member)
        await self._session.commit()
        await self._session.refresh(member)
        return member

    async def update(self, member: CommitteeMember, data: CommitteeMemberCreate) -> CommitteeMember:
        member.event_id = data.event_id
        member.person_id = data.person_id
        member.role = data.role
        member.committee_type = data.committee_type
        member.sort_order = data.sort_order
        await self._session.commit()
        await self._session.refresh(member)
        return member

    async def delete(self, member: CommitteeMember) -> None:
        await self._session.delete(member)
        await self._session.commit()
