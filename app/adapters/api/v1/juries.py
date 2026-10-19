from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.api.dependencies import get_jury_service
from app.schemas import JuryCreate, JuryProgressItem, JuryRead, JuryUpdate
from app.services.jury import JuryService

router = APIRouter(tags=["juries"])


@router.get("/", response_model=list[JuryRead])
async def list_juries(
    service: Annotated[JuryService, Depends(get_jury_service)],
    university_id: int | None = Query(default=None, description="Filter by university ID"),
    is_chairman: bool | None = Query(default=None, description="Filter by chairman role"),
) -> list[JuryRead]:
    juries = await service.list_juries(university_id=university_id, is_chairman=is_chairman)
    return [JuryRead.model_validate(jury) for jury in juries]


@router.get("/{jury_id}", response_model=JuryRead)
async def get_jury(
    jury_id: int,
    service: Annotated[JuryService, Depends(get_jury_service)],
) -> JuryRead:
    jury = await service.get_jury_by_id(jury_id)
    if jury is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jury member with id {jury_id} not found",
        )
    return JuryRead.model_validate(jury)


@router.get("/{jury_id}/progress", response_model=list[JuryProgressItem])
async def get_jury_progress(
    jury_id: int,
    service: Annotated[JuryService, Depends(get_jury_service)],
) -> list[JuryProgressItem]:
    return await service.get_jury_progress(jury_id)


@router.post("/", response_model=JuryRead, status_code=status.HTTP_201_CREATED)
async def create_jury(
    payload: JuryCreate,
    service: Annotated[JuryService, Depends(get_jury_service)],
) -> JuryRead:
    jury = await service.create_jury(payload)
    return JuryRead.model_validate(jury)


@router.patch("/{jury_id}", response_model=JuryRead)
async def update_jury(
    jury_id: int,
    payload: JuryUpdate,
    service: Annotated[JuryService, Depends(get_jury_service)],
) -> JuryRead:
    jury = await service.update_jury(jury_id, payload)
    if jury is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jury member with id {jury_id} not found",
        )
    return JuryRead.model_validate(jury)


@router.delete("/{jury_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_jury(
    jury_id: int,
    service: Annotated[JuryService, Depends(get_jury_service)],
) -> None:
    deleted = await service.delete_jury(jury_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jury member with id {jury_id} not found",
        )
