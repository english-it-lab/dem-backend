from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Event, Organizer
from app.schemas import EventCreate


class EventRepository:
    """Data access layer for events."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_events(self) -> Sequence[Event]:
        stmt = select(Event).order_by(Event.name)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_event(self, data: EventCreate) -> Event:
        event = Event(
            venue_id=data.venue_id,
            organizer_id=data.organizer_id,
            name=data.name,
            type=data.type,
            event_date=data.event_date,
        )

        self._session.add(event)

        await self._session.commit()
        await self._session.flush()

        return event

    async def get_event_with_organizer(self, event_id: int) -> Event | None:
        stmt = (
            select(Event)
            .options(
                selectinload(Event.venue),
                selectinload(Event.organizer).selectinload(Organizer.person),
            )
            .where(Event.id == event_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
