from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Jury, SectionJury


class SectionJuryRepository:
    """Data access layer for section-jury assignments."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_assignments(
        self,
        *,
        section_id: int | None = None,
        jury_id: int | None = None,
    ) -> Sequence[SectionJury]:
        """Return all assignments optionally filtered by section or jury."""
        stmt = select(SectionJury).order_by(SectionJury.id)
        if section_id is not None:
            stmt = stmt.where(SectionJury.section_id == section_id)
        if jury_id is not None:
            stmt = stmt.where(SectionJury.jury_id == jury_id)

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_assignment_by_id(self, assignment_id: int) -> SectionJury | None:
        """Return assignment by its primary key."""
        stmt = select(SectionJury).where(SectionJury.id == assignment_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_assignment_by_pair(self, *, section_id: int, jury_id: int) -> SectionJury | None:
        """Return assignment for the provided section/jury pair."""
        stmt = select(SectionJury).where(SectionJury.section_id == section_id, SectionJury.jury_id == jury_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_assignment(self, *, section_id: int, jury_id: int) -> SectionJury:
        """Persist new section/jury mapping."""
        assignment = SectionJury(section_id=section_id, jury_id=jury_id)
        self._session.add(assignment)
        await self._session.flush()
        await self._session.refresh(assignment)
        return assignment

    async def update_assignment(self, assignment: SectionJury, *, section_id: int, jury_id: int) -> SectionJury:
        """Update mapping values."""
        assignment.section_id = section_id
        assignment.jury_id = jury_id
        await self._session.flush()
        await self._session.refresh(assignment)
        return assignment

    async def delete_assignment(self, assignment: SectionJury) -> None:
        """Delete the provided assignment."""
        await self._session.delete(assignment)
        await self._session.flush()

    async def is_jury_assigned_to_section(self, jury_id: int, section_id: int) -> bool:
        """
        Check if a jury member is assigned to a specific section.

        Args:
            jury_id: ID of the jury member
            section_id: ID of the section

        Returns:
            True if assignment exists, False otherwise
        """
        stmt = select(SectionJury).where(SectionJury.jury_id == jury_id, SectionJury.section_id == section_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_by_section_with_jury(self, section_id: int) -> Sequence[SectionJury]:
        stmt = (
            select(SectionJury)
            .where(SectionJury.section_id == section_id)
            .options(
                selectinload(SectionJury.jury).selectinload(Jury.person),
                selectinload(SectionJury.jury).selectinload(Jury.university),
            )
            .order_by(SectionJury.id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
