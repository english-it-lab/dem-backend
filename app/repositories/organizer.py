from collections.abc import Sequence

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Organizer
from app.schemas import OrganizerCreate


class OrganizerRepository:
    """Data access layer for organizer management."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists_by_id(self, organizer_id: int) -> bool:
        stmt = select(exists().where(Organizer.id == organizer_id))
        return await self._session.scalar(stmt)

    async def exists_by_person_id(self, person_id: int) -> bool:
        stmt = select(exists().where(Organizer.person_id == person_id))
        return await self._session.scalar(stmt)

    async def list_organizers(self) -> Sequence[Organizer]:
        stmt = select(Organizer).options(selectinload(Organizer.person)).order_by(Organizer.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_organizer_by_id(self, organizer_id: int) -> Organizer | None:
        stmt = select(Organizer).where(Organizer.id == organizer_id).options(selectinload(Organizer.person))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_organizer(self, data: OrganizerCreate) -> Organizer:
        organizer = Organizer(
            person_id=data.person_id,
            contact_number=data.contact_number,
            access_key=data.access_key,
        )
        self._session.add(organizer)
        await self._session.commit()
        await self._session.refresh(organizer)
        return organizer

    async def update_organizer(self, organizer: Organizer, data: OrganizerCreate) -> Organizer:
        organizer.person_id = data.person_id
        organizer.contact_number = data.contact_number
        organizer.access_key = data.access_key
        await self._session.commit()
        await self._session.refresh(organizer)
        return organizer

    async def delete_organizer(self, organizer: Organizer) -> None:
        await self._session.delete(organizer)
        await self._session.commit()
