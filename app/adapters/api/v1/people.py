from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.api.dependencies import get_person_service
from app.schemas import PersonCreate, PersonRead
from app.services.person import PersonService

router = APIRouter(tags=["people"])


@router.get("/", response_model=list[PersonRead])
async def list_people(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    service: Annotated[PersonService, Depends(get_person_service)] = None,
) -> list[PersonRead]:
    people = await service.list_people(skip, limit)
    return [PersonRead.model_validate(p) for p in people]


@router.get("/{person_id}", response_model=PersonRead)
async def get_person(
    person_id: int,
    service: Annotated[PersonService, Depends(get_person_service)],
) -> PersonRead:
    person = await service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Человек не найден")
    return PersonRead.model_validate(person)


@router.post("/", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
async def create_person(
    payload: PersonCreate,
    service: Annotated[PersonService, Depends(get_person_service)],
) -> PersonRead:
    person = await service.create_person(payload)
    return PersonRead.model_validate(person)


@router.put("/{person_id}", response_model=PersonRead)
async def update_person(
    person_id: int,
    payload: PersonCreate,
    service: Annotated[PersonService, Depends(get_person_service)],
) -> PersonRead:
    try:
        person = await service.update_person(person_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return PersonRead.model_validate(person)


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: int,
    service: Annotated[PersonService, Depends(get_person_service)],
) -> None:
    try:
        await service.delete_person(person_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
