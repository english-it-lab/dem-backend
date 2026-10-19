from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.adapters.api.dependencies import get_current_user, get_person_service
from app.schemas import PersonMyselfUpdate, PersonRead, PersonUpdate
from app.services.person import PersonService

router = APIRouter(tags=["person"])


@router.put("/", response_model=PersonRead, status_code=status.HTTP_200_OK)
async def put_person(
    payload: PersonUpdate,
    service: Annotated[PersonService, Depends(get_person_service)],
    _person_id: Annotated[int, Depends(get_current_user)],
) -> PersonRead:
    return await service.put_person(payload)


@router.post("/", response_model=PersonRead, status_code=status.HTTP_200_OK)
async def create_person(
    payload: PersonUpdate,
    service: Annotated[PersonService, Depends(get_person_service)],
    _person_id: Annotated[int, Depends(get_current_user)],
) -> PersonRead:
    return await service.create_person(payload)


@router.patch("/", response_model=PersonRead, status_code=status.HTTP_200_OK)
async def update_yours_person_data(
    payload: PersonMyselfUpdate,
    service: Annotated[PersonService, Depends(get_person_service)],
    _person_id: Annotated[int, Depends(get_current_user)],
) -> PersonRead:
    data = payload.model_dump()
    data["id"] = _person_id
    return await service.update_person(PersonUpdate(**data))


@router.get("/", response_model=PersonRead, status_code=status.HTTP_200_OK)
async def get_person_by_id(
    person_id: int,
    service: Annotated[PersonService, Depends(get_person_service)],
    _person_id: Annotated[int, Depends(get_current_user)],
) -> PersonRead:
    return await service.get_person_by_id(person_id)


@router.get("/me", response_model=PersonRead, status_code=status.HTTP_200_OK)
async def get_person_data_from_jwt(
    service: Annotated[PersonService, Depends(get_person_service)],
    _person_id: Annotated[int, Depends(get_current_user)],
) -> PersonRead:
    return await service.get_person_by_id(_person_id)
