from collections.abc import Sequence

from fastapi import HTTPException, status

from app.models import Jury
from app.repositories.jury import JuryRepository
from app.repositories.person import PersonRepository
from app.repositories.university import UniversityRepository
from app.schemas import JuryCreate, JuryProgressItem, JuryUpdate


class JuryService:
    """Business logic for jury entities."""

    def __init__(
        self,
        jury_repository: JuryRepository,
        university_repository: UniversityRepository,
        person_repository: PersonRepository,
    ) -> None:
        self._jury_repository = jury_repository
        self._university_repository = university_repository
        self._person_repository = person_repository

    async def list_juries(
        self,
        university_id: int | None = None,
        is_chairman: bool | None = None,
    ) -> Sequence[Jury]:
        return await self._jury_repository.list_juries(
            university_id=university_id,
            is_chairman=is_chairman,
        )

    async def get_jury_by_id(self, jury_id: int) -> Jury | None:
        return await self._jury_repository.get_jury_by_id(jury_id)

    async def create_jury(self, payload: JuryCreate) -> Jury:
        if payload.university_id is not None:
            university = await self._university_repository.get_university_by_id(payload.university_id)
            if university is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"University with id {payload.university_id} not found",
                )

        if payload.person_id is not None:
            person = await self._person_repository.get_person_by_id(payload.person_id)
            if person is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Person with id {payload.person_id} not found",
                )

        return await self._jury_repository.create_jury(payload)

    async def update_jury(self, jury_id: int, payload: JuryUpdate) -> Jury | None:
        jury = await self._jury_repository.get_jury_by_id(jury_id)
        if jury is None:
            return None

        update_data = payload.model_dump(exclude_unset=True)

        if "university_id" in update_data and update_data["university_id"] is not None:
            university = await self._university_repository.get_university_by_id(update_data["university_id"])
            if university is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"University with id {update_data['university_id']} not found",
                )

        if "person_id" in update_data and update_data["person_id"] is not None:
            person = await self._person_repository.get_person_by_id(update_data["person_id"])
            if person is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Person with id {update_data['person_id']} not found",
                )

        return await self._jury_repository.update_jury(jury, payload)

    async def delete_jury(self, jury_id: int) -> bool:
        jury = await self._jury_repository.get_jury_by_id(jury_id)
        if jury is None:
            return False

        await self._jury_repository.delete_jury(jury)
        return True

    async def get_jury_progress(self, jury_id: int) -> list[JuryProgressItem]:
        jury = await self._jury_repository.get_jury_by_id(jury_id)
        if jury is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Jury member with id {jury_id} not found",
            )

        raw_data = await self._jury_repository.get_jury_progress(jury_id)

        result = []
        for row in raw_data:
            full_name = f"{row.last_name} {row.first_name}".strip()

            result.append(
                JuryProgressItem(
                    participant_id=row.participant_id,
                    participant_name=full_name,
                    topic=row.presentation_topic,
                    is_graded=row.is_graded,
                    current_score=row.current_score if row.is_graded else None,
                )
            )

        return result
