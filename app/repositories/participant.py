from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Faculty, GroupParticipant, Participant
from app.schemas import ParticipantCreate, ParticipantUpdate


class ParticipantRepository:
    """Data access layer for participants."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_participant(self, person_id: int, section_id: int, is_group_leader: bool) -> Participant:
        participant = Participant(person_id=person_id, section_id=section_id, is_group_leader=is_group_leader)
        self._session.add(participant)

        await self._session.flush()
        await self._session.refresh(participant)
        return participant

    async def list_participants(self, skip: int = 0, limit: int = 100) -> Sequence[Participant]:
        """Get a list of participants with pagination."""
        stmt = select(Participant).order_by(Participant.id).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_participants_by_group_id(self, group_id: int) -> Sequence[Participant]:
        stmt = (
            select(Participant)
            .join(GroupParticipant, GroupParticipant.participant_id == Participant.id)
            .where(GroupParticipant.group_id == group_id)
        )

        result = await self._session.execute(stmt)
        return result.scalars().unique().all()

    async def get_participant_by_id(self, participant_id: int) -> Participant | None:
        """
        Retrieve a participant by ID.

        Args:
            participant_id: ID of the participant

        Returns:
            Participant instance or None if not found
        """
        stmt = select(Participant).where(Participant.id == participant_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_participants_by_section(self, section_id: int) -> Sequence[Participant]:
        stmt = (
            select(Participant)
            .where(Participant.section_id == section_id)
            .options(
                selectinload(Participant.person),
                selectinload(Participant.faculty).selectinload(Faculty.university),
                selectinload(Participant.scientific_advisor),
            )
            .order_by(Participant.presentation_order, Participant.id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_full_participant(self, data: ParticipantCreate) -> Participant | None:
        """
        Create a new participant.
        """
        participant = Participant(
            person_id=data.person_id,
            faculty_id=data.faculty_id,
            course_id=data.course_id,
            teacher_id=data.teacher_id,
            section_id=data.section_id,
            is_poster_participant=data.is_poster_participant,
            is_translator_participant=data.is_translator_participant,
            has_translator_education=data.has_translator_education,
            textbook_level_id=data.textbook_level_id,
            is_group_leader=data.is_group_leader,
            presentation_topic=data.presentation_topic,
            is_notification_allowed=data.is_notification_allowed,
            password_hash=data.password_hash,
        )
        self._session.add(participant)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(participant)
        return participant

    async def update_participant(self, participant_id: int, data: ParticipantUpdate) -> Participant | None:
        """
        Update participant details.
        """
        participant = await self.get_participant_by_id(participant_id)
        if not participant:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(participant, field, value)

        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(participant)
        return participant

    async def delete_participant(self, participant_id: int) -> bool:
        """Delete a participant by ID."""
        participant = await self.get_participant_by_id(participant_id)
        if not participant:
            return False

        await self._session.delete(participant)
        await self._session.commit()
        return True
