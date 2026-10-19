from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.adapters.api.dependencies import get_organizer_service
from app.schemas import OrganizerCreate, OrganizerRead
from app.services.organizer import OrganizerService

router = APIRouter(tags=["organizers"])


@router.get("/", response_model=list[OrganizerRead])
async def list_organizers(
    service: Annotated[OrganizerService, Depends(get_organizer_service)],
) -> list[OrganizerRead]:
    organizers = await service.list_organizers()
    return [OrganizerRead.model_validate(o) for o in organizers]


@router.get("/{organizer_id}", response_model=OrganizerRead)
async def get_organizer(
    organizer_id: int,
    service: Annotated[OrganizerService, Depends(get_organizer_service)],
) -> OrganizerRead:
    organizer = await service.get_organizer(organizer_id)
    if not organizer:
        raise HTTPException(status_code=404, detail="Организатор не найден")
    return OrganizerRead.model_validate(organizer)


@router.post("/", response_model=OrganizerRead, status_code=status.HTTP_201_CREATED)
async def create_organizer(
    payload: OrganizerCreate,
    service: Annotated[OrganizerService, Depends(get_organizer_service)],
) -> OrganizerRead:
    organizer = await service.create_organizer(payload)
    return OrganizerRead.model_validate(organizer)


@router.put("/{organizer_id}", response_model=OrganizerRead)
async def update_organizer(
    organizer_id: int,
    payload: OrganizerCreate,
    service: Annotated[OrganizerService, Depends(get_organizer_service)],
) -> OrganizerRead:
    try:
        organizer = await service.update_organizer(organizer_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return OrganizerRead.model_validate(organizer)


@router.delete("/{organizer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organizer(
    organizer_id: int,
    service: Annotated[OrganizerService, Depends(get_organizer_service)],
) -> None:
    try:
        await service.delete_organizer(organizer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
