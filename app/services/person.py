from fastapi import HTTPException, status

from app.models import Person
from app.repositories.person import PersonRepository
from app.schemas import PersonRead, PersonUpdate


class PersonService:
    """Business logic for jury score operations."""

    def __init__(self, person_repository: PersonRepository) -> None:
        self._person_repository = person_repository

    async def get_person_by_id(self, person_id: int) -> PersonRead:
        """
        Retrieve person data by id.
        """
        # Validate person exists
        person = await self._person_repository.get_person_by_id(person_id)
        if person is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person with id {person_id} not found",
            )

        return PersonRead.model_validate(person)

    async def put_person(self, person_payload: PersonUpdate) -> PersonRead:
        """
        Put person data
        """

        person = Person(**person_payload.model_dump())
        person = await self._person_repository.put_person(person)

        return PersonRead.model_validate(person)

    async def update_person(self, person_payload: PersonUpdate) -> PersonRead:
        """
        Update person data, if it exists
        """
        if await self._person_repository.get_person_by_id(person_payload.id) is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Person with id {person_payload.id} doesn't exist",
            )

        return PersonRead.model_validate(await self.put_person(person_payload))

    async def create_person(self, person_payload: PersonUpdate) -> PersonRead:
        """
        Create person, if doesn't it exists
        """
        if await self._person_repository.get_person_by_id(person_payload.id) is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Person with id {person_payload.id} doesn't exist",
            )

        return PersonRead.model_validate(await self.put_person(person_payload))
