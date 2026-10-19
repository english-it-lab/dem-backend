from collections.abc import Sequence

from app.models import Venue
from app.repositories.venues import VenueRepository
from app.schemas import VenueCreate


class VenuesService:
    def __init__(self, repository: VenueRepository) -> None:
        self._repository = repository

    async def list_venues(self) -> Sequence[Venue]:
        return await self._repository.list_venues()

    async def create_venue(self, payload: VenueCreate) -> Venue:
        return await self._repository.create_venue(payload)
