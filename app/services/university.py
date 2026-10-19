from collections.abc import Sequence

from app.models import University
from app.repositories.university import UniversityRepository
from app.schemas import UniversityCreate


class UniversityService:
    """Business logic for university entities."""

    def __init__(self, repository: UniversityRepository) -> None:
        self._repository = repository

    async def list_universities(self) -> Sequence[University]:
        return await self._repository.list_universities()

    async def create_university(self, payload: UniversityCreate) -> University:
        return await self._repository.create_university(payload)
