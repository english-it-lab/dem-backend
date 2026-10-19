from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Venue
from app.schemas import VenueCreate


class VenueRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_venues(self) -> Sequence[Venue]:
        stmt = select(Venue)
        stmt = stmt.order_by(Venue.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_venue(self, data: VenueCreate) -> Venue:
        venue = Venue(city=data.city, street=data.street, building=data.building)
        self._session.add(venue)
        await self._session.commit()
        await self._session.flush()
        return venue
