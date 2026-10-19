from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.adapters.api.dependencies import get_draw_service
from app.schemas import DrawResultRead, DrawRunResult
from app.services.draw import DrawService

router = APIRouter(tags=["Draw"])

SectionIdQuery = Annotated[int, Query(alias="sectionId", ge=1)]
DrawServiceDep = Annotated[DrawService, Depends(get_draw_service)]


@router.post("/draw/run", response_model=DrawRunResult)
async def run_draw(section_id: SectionIdQuery, service: DrawServiceDep) -> DrawRunResult:
    """Randomly assign the section's topics to its groups. Replaces the previous draw."""
    return await service.run_draw(section_id)


@router.get("/draw-results", response_model=list[DrawResultRead])
async def get_draw_results(section_id: SectionIdQuery, service: DrawServiceDep) -> list[DrawResultRead]:
    """Return the current topic assignment for the section's groups."""
    return await service.get_results(section_id)
