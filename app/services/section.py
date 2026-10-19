from collections.abc import Sequence

from fastapi import HTTPException, status

from app.models import Section
from app.repositories.event import EventRepository
from app.repositories.organizer import OrganizerRepository
from app.repositories.section import SectionRepository
from app.schemas import SectionCreate, SectionUpdate


class SectionService:
    """Business logic for section entities."""

    def __init__(
        self,
        repository: SectionRepository,
        organizer_repository: OrganizerRepository,
        event_repository: EventRepository,
    ) -> None:
        self._repository = repository
        self._organizer_repository = organizer_repository
        self._event_repository = event_repository

    async def list_sections(self, skip: int = 0, limit: int = 100) -> Sequence[Section]:
        """Get a list of sections with pagination."""
        return await self._repository.list_sections(skip, limit)

    async def get_section_by_id(self, section_id: int) -> Section | None:
        """Get a specific section by ID."""
        section = await self._repository.get_section_by_id(section_id)
        if section is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return section

    async def create_section(self, data: SectionCreate) -> Section:
        """
        Create a new section.
        If event_id is provided, creates a link in event_sections table.
        """
        if data.name is None or len(data.name) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Section name cannot be null or empty")
        if data.lecture_hall is None or len(data.lecture_hall) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lecture hall cannot be null or empty")
        if data.event_id and not await self._event_repository.exists_by_id(data.event_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with id {data.event_id} not found"
            )

        return await self._repository.create_section(data)

    async def update_section(self, section_id: int, data: SectionUpdate) -> Section:
        """
        Update section details.
        Logs the change in organizer_section_changes if organizer_id is provided.
        """
        if data.organizer_id and not await self._organizer_repository.exists_by_id(data.organizer_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Organizer with id {data.organizer_id} not found"
            )

        section = await self._repository.update_section(section_id, data)
        if section is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return section

    async def delete_section(self, section_id: int) -> None:
        """Delete a section by ID."""
        if not await self._repository.delete_section(section_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
