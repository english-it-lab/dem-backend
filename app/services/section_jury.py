from __future__ import annotations

from collections.abc import Sequence

from fastapi import HTTPException, status

from app.models import SectionJury
from app.repositories.jury import JuryRepository
from app.repositories.section import SectionRepository
from app.repositories.section_jury import SectionJuryRepository
from app.schemas import SectionJuryCreate, SectionJuryUpdate


class SectionJuryService:
    """Business logic for assigning jury members to sections."""

    def __init__(
        self,
        section_jury_repository: SectionJuryRepository,
        section_repository: SectionRepository,
        jury_repository: JuryRepository,
    ) -> None:
        self._repository = section_jury_repository
        self._section_repository = section_repository
        self._jury_repository = jury_repository

    async def list_assignments(
        self,
        *,
        section_id: int | None = None,
        jury_id: int | None = None,
    ) -> Sequence[SectionJury]:
        return await self._repository.list_assignments(section_id=section_id, jury_id=jury_id)

    async def get_assignment_by_id(self, assignment_id: int) -> SectionJury | None:
        return await self._repository.get_assignment_by_id(assignment_id)

    async def create_assignment(self, payload: SectionJuryCreate) -> SectionJury:
        await self._validate_section_exists(payload.section_id)
        await self._validate_jury_exists(payload.jury_id)

        existing = await self._repository.get_assignment_by_pair(
            section_id=payload.section_id,
            jury_id=payload.jury_id,
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="This jury member is already assigned to the section",
            )

        return await self._repository.create_assignment(section_id=payload.section_id, jury_id=payload.jury_id)

    async def update_assignment(self, assignment_id: int, payload: SectionJuryUpdate) -> SectionJury | None:
        assignment = await self._repository.get_assignment_by_id(assignment_id)
        if assignment is None:
            return None

        new_section_id = payload.section_id or assignment.section_id
        new_jury_id = payload.jury_id or assignment.jury_id

        if payload.section_id is not None:
            await self._validate_section_exists(payload.section_id)
        if payload.jury_id is not None:
            await self._validate_jury_exists(payload.jury_id)

        if (new_section_id != assignment.section_id) or (new_jury_id != assignment.jury_id):
            duplicate = await self._repository.get_assignment_by_pair(
                section_id=new_section_id,
                jury_id=new_jury_id,
            )
            if duplicate is not None and duplicate.id != assignment.id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="This jury member is already assigned to the section",
                )

        return await self._repository.update_assignment(
            assignment,
            section_id=new_section_id,
            jury_id=new_jury_id,
        )

    async def delete_assignment(self, assignment_id: int) -> bool:
        assignment = await self._repository.get_assignment_by_id(assignment_id)
        if assignment is None:
            return False

        await self._repository.delete_assignment(assignment)
        return True

    async def _validate_section_exists(self, section_id: int) -> None:
        section = await self._section_repository.get_section_by_id(section_id)
        if section is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section with id {section_id} not found",
            )

    async def _validate_jury_exists(self, jury_id: int) -> None:
        jury = await self._jury_repository.get_jury_by_id(jury_id)
        if jury is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Jury member with id {jury_id} not found",
            )
