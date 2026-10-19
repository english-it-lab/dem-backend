from collections.abc import Sequence

from app.models import Organizer
from app.repositories.organizer import OrganizerRepository
from app.schemas import OrganizerCreate


class OrganizerService:
    """Business logic for organizers."""

    def __init__(self, repository: OrganizerRepository) -> None:
        self._repository = repository

    async def list_organizers(self) -> Sequence[Organizer]:
        return await self._repository.list_organizers()

    async def get_organizer(self, organizer_id: int) -> Organizer | None:
        return await self._repository.get_organizer_by_id(organizer_id)

    async def create_organizer(self, payload: OrganizerCreate) -> Organizer:
        return await self._repository.create_organizer(payload)

    async def update_organizer(self, organizer_id: int, payload: OrganizerCreate) -> Organizer:
        organizer = await self._repository.get_organizer_by_id(organizer_id)
        if not organizer:
            raise ValueError(f"Организатор {organizer_id} не найден")
        return await self._repository.update_organizer(organizer, payload)

    async def delete_organizer(self, organizer_id: int) -> None:
        organizer = await self._repository.get_organizer_by_id(organizer_id)
        if not organizer:
            raise ValueError(f"Организатор {organizer_id} не найден")
        await self._repository.delete_organizer(organizer)
