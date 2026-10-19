from collections.abc import Sequence

from fastapi import HTTPException, status

from app.models import Participant
from app.repositories.course import CourseRepository
from app.repositories.faculty import FacultyRepository
from app.repositories.participant import ParticipantRepository
from app.repositories.person import PersonRepository
from app.repositories.section import SectionRepository
from app.repositories.teacher import TeacherRepository
from app.repositories.textbook_level import TextbookLevelRepository
from app.schemas import ParticipantCreate, ParticipantUpdate


class ParticipantService:
    """Business logic for participant entities."""

    def __init__(
        self,
        repository: ParticipantRepository,
        faculty_repository: FacultyRepository,
        course_repository: CourseRepository,
        teacher_repository: TeacherRepository,
        section_repository: SectionRepository,
        person_repository: PersonRepository,
        textbook_level_repository: TextbookLevelRepository,
    ) -> None:
        self._repository = repository
        self._faculty_repository = faculty_repository
        self._course_repository = course_repository
        self._teacher_repository = teacher_repository
        self._section_repository = section_repository
        self._person_repository = person_repository
        self._textbook_level_repository = textbook_level_repository

    async def list_participants(self, skip: int = 0, limit: int = 100) -> Sequence[Participant]:
        """Get a list of participants with pagination."""
        return await self._repository.list_participants(skip, limit)

    async def get_participant_by_id(self, participant_id: int) -> Participant | None:
        """Get a specific participant by ID."""
        participant = await self._repository.get_participant_by_id(participant_id)
        if participant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return participant

    async def create_participant(self, data: ParticipantCreate) -> Participant:
        """
        Create a new participant.
        If event_id is provided, creates a link in event_sections table.
        """
        if data.person_id is None or data.person_id == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Person id cannot be null or empty")
        return await self._repository.create_full_participant(data)

    async def update_participant(self, participant_id: int, data: ParticipantUpdate) -> Participant:
        """
        Update participant details.
        """
        # if data.faculty_id and not await self._faculty_repository.exists_by_id(data.faculty_id):
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail=f"Faculty with id {data.faculty_id} not found"
        #     )
        # if data.course_id and not await self._course_repository.exists_by_id(data.course_id):
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail=f"Course with id {data.course_id} not found"
        #     )
        # if data.teacher_id and not await self._teacher_repository.exists_by_id(data.teacher_id):
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail=f"Teacher with id {data.teacher_id} not found"
        #     )
        # if data.section_id and not await self._section_repository.exists_by_id(data.section_id):
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail=f"Section with id {data.section_id} not found"
        #     )
        # if data.person_id and not await self._person_repository.exists_by_id(data.person_id):
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail=f"Person with id {data.person_id} not found"
        #     )
        # if data.textbook_level_id and
        # not await self._text_book_level_repository.exists_by_id(data.textbook_level_id):
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Text book level with id {data.textbook_level_id} not found",
        #     )

        participant = await self._repository.update_participant(participant_id, data)
        if participant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return participant

    async def delete_participant(self, participant_id: int) -> None:
        """Delete a participant by ID."""
        if not await self._repository.delete_participant(participant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
