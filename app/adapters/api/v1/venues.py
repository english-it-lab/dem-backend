from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.adapters.api.dependencies import get_venue_service
from app.schemas import VenueCreate, VenueRead
from app.services.venue import VenueService

router = APIRouter(tags=["venues"])


@router.get("/", response_model=list[VenueRead])
async def list_venues(
    service: Annotated[VenueService, Depends(get_venue_service)],
) -> list[VenueRead]:
    venues = await service.list_venues()
    return [VenueRead.model_validate(venue) for venue in venues]


@router.post("/", response_model=VenueRead, status_code=status.HTTP_201_CREATED)
async def create_venue(
    payload: VenueCreate,
    service: Annotated[VenueService, Depends(get_venue_service)],
) -> VenueRead:
    venue = await service.create_venue(payload)
    return VenueRead.model_validate(venue)
