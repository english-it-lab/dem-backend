from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.api.dependencies import get_section_jury_service
from app.schemas import SectionJuryCreate, SectionJuryRead, SectionJuryUpdate
from app.services.section_jury import SectionJuryService

router = APIRouter(tags=["section-juries"])


@router.get("/", response_model=list[SectionJuryRead])
async def list_section_juries(
    service: Annotated[SectionJuryService, Depends(get_section_jury_service)],
    section_id: Annotated[int | None, Query()] = None,
    jury_id: Annotated[int | None, Query()] = None,
) -> list[SectionJuryRead]:
    assignments = await service.list_assignments(section_id=section_id, jury_id=jury_id)
    return [SectionJuryRead.model_validate(assignment) for assignment in assignments]


@router.get("/{assignment_id}", response_model=SectionJuryRead)
async def get_section_jury(
    assignment_id: int,
    service: Annotated[SectionJuryService, Depends(get_section_jury_service)],
) -> SectionJuryRead:
    assignment = await service.get_assignment_by_id(assignment_id)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section jury assignment with id {assignment_id} not found",
        )
    return SectionJuryRead.model_validate(assignment)


@router.post("/", response_model=SectionJuryRead, status_code=status.HTTP_201_CREATED)
async def create_section_jury(
    payload: SectionJuryCreate,
    service: Annotated[SectionJuryService, Depends(get_section_jury_service)],
) -> SectionJuryRead:
    assignment = await service.create_assignment(payload)
    return SectionJuryRead.model_validate(assignment)


@router.patch("/{assignment_id}", response_model=SectionJuryRead)
async def update_section_jury(
    assignment_id: int,
    payload: SectionJuryUpdate,
    service: Annotated[SectionJuryService, Depends(get_section_jury_service)],
) -> SectionJuryRead:
    assignment = await service.update_assignment(assignment_id, payload)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section jury assignment with id {assignment_id} not found",
        )
    return SectionJuryRead.model_validate(assignment)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section_jury(
    assignment_id: int,
    service: Annotated[SectionJuryService, Depends(get_section_jury_service)],
) -> None:
    deleted = await service.delete_assignment(assignment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section jury assignment with id {assignment_id} not found",
        )
