from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event


class EventRepository:
    """Data access layer for event management."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists_by_id(self, event_id: int) -> bool:
        """Checks the existence of a record in the table."""
        stmt = select(exists().where(Event.id == event_id))
        return await self._session.scalar(stmt)
