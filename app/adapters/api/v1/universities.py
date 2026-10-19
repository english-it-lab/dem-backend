from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.adapters.api.dependencies import get_university_service
from app.schemas import UniversityCreate, UniversityRead
from app.services.university import UniversityService

router = APIRouter(tags=["universities"])


@router.get("/", response_model=list[UniversityRead])
async def list_universities(
    service: Annotated[UniversityService, Depends(get_university_service)],
) -> list[UniversityRead]:
    universities = await service.list_universities()
    return [UniversityRead.model_validate(university) for university in universities]


@router.post("/", response_model=UniversityRead, status_code=status.HTTP_201_CREATED)
async def create_university(
    payload: UniversityCreate,
    service: Annotated[UniversityService, Depends(get_university_service)],
) -> UniversityRead:
    university = await service.create_university(payload)
    return UniversityRead.model_validate(university)
