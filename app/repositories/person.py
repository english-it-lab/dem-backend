from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Person


class PersonRepository:
    """Data access layer for people."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_people(self, skip: int = 0, limit: int = 100) -> Sequence[Person]:
        stmt = select(Person).order_by(Person.last_name, Person.first_name).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_person_by_id(self, person_id: int) -> Person | None:
        stmt = select(Person).where(Person.id == person_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    """
        CREATES OR UPDATES PERSON ENTITY
    """

    async def put_person(self, person: Person) -> Person:
        merged = await self._session.merge(person)
        await self._session.commit()
        await self._session.refresh(merged)
        return merged

    async def get_person_by_email(self, email: str) -> Person | None:
        stmt = select(Person).where(Person.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_person(self, email: str) -> Person:
        person = Person(email=email)

        self._session.add(person)

        await self._session.flush()
        await self._session.refresh(person)
        return person
