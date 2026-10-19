from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroupParticipant, Participant


class GroupParticipantRepository:
    """Data access layer for group participants."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_group_participant(self, group_id: int, participant_id: int) -> GroupParticipant:
        group_participant = GroupParticipant(group_id=group_id, participant_id=participant_id)
        self._session.add(group_participant)

        await self._session.flush()
        await self._session.refresh(group_participant)
        return group_participant

    async def get_participant_by_group_and_person(self, group_id: int, person_id: int) -> Participant | None:
        stmt = (
            select(Participant)
            .join(GroupParticipant, GroupParticipant.participant_id == Participant.id)
            .where(GroupParticipant.group_id == group_id, Participant.person_id == person_id)
        )

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
