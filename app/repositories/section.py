from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventSection, OrganizerSectionChange, Section
from app.schemas import SectionCreate, SectionUpdate


class SectionRepository:
    """Data access layer for sections management."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_sections(self, skip: int = 0, limit: int = 100) -> Sequence[Section]:
        """Get a list of sections with pagination."""
        stmt = select(Section).order_by(Section.id).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_section_by_id(self, section_id: int) -> Section | None:
        """Get a specific section by ID."""
        stmt = select(Section).where(Section.id == section_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_section(self, data: SectionCreate) -> Section:
        """
        Create a new section.
        If event_id is provided, creates a link in event_sections table.
        """
        section = Section(name=data.name, lecture_hall=data.lecture_hall, time=data.time)
        self._session.add(section)
        await self._session.flush()

        if data.event_id:
            event_link = EventSection(event_id=data.event_id, section_id=section.id)
            self._session.add(event_link)

        await self._session.commit()
        await self._session.refresh(section)
        return section

    async def update_section(self, section_id: int, data: SectionUpdate) -> Section | None:
        """
        Update section details.
        Logs the change in organizer_section_changes if organizer_id is provided.
        """
        section = await self.get_section_by_id(section_id)
        if not section:
            return None

        update_values = data.model_dump(exclude_unset=True)
        organizer_id = update_values.pop("organizer_id", None)

        if not update_values:
            return section

        for key, value in update_values.items():
            setattr(section, key, value)

        if organizer_id is not None:
            change_log = OrganizerSectionChange(section_id=section.id, organizer_id=organizer_id)
            self._session.add(change_log)

        await self._session.commit()
        await self._session.refresh(section)
        return section

    async def delete_section(self, section_id: int) -> bool:
        """Delete a section by ID."""
        section = await self.get_section_by_id(section_id)
        if not section:
            return False

        await self._session.delete(section)
        await self._session.commit()
        return True

    async def get_sections_by_event(self, event_id: int) -> Sequence[Section]:
        stmt = (
            select(Section)
            .join(EventSection, Section.id == EventSection.section_id)
            .where(EventSection.event_id == event_id)
            .order_by(Section.time)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
