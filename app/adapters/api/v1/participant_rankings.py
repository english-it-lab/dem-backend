from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.api.dependencies import get_participant_ranking_service
from app.schemas import (
    ParticipantRankingList,
    ParticipantRankingRead,
    ParticipantRankingSortField,
    SortOrder,
)
from app.services.participant_ranking import ParticipantRankingService

router = APIRouter(tags=["participant-rankings"])


@router.get("/", response_model=ParticipantRankingList)
async def list_participant_rankings(
    service: Annotated[ParticipantRankingService, Depends(get_participant_ranking_service)],
    page: Annotated[int, Query(ge=1, description="Page number starting from 1")] = 1,
    page_size: Annotated[int, Query(ge=1, le=200, description="Items per page")] = 25,
    section_id: Annotated[int | None, Query(description="Filter by section id")] = None,
    jury_id: Annotated[int | None, Query(description="Filter by jury section assignment")] = None,
    sort_by: Annotated[
        ParticipantRankingSortField,
        Query(description="Field to sort by"),
    ] = ParticipantRankingSortField.TOTAL_SCORE,
    sort_order: Annotated[
        SortOrder,
        Query(description="Sorting direction"),
    ] = SortOrder.DESC,
) -> ParticipantRankingList:
    """
    Aggregated leaderboard for participants with pagination, filtering, and sorting.

    By default, the list is sorted by the total score (descending) with alphabetical
    tie-breaking to satisfy the tech requirements.
    """
    return await service.list_rankings(
        section_id=section_id,
        jury_id=jury_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{participant_id}", response_model=ParticipantRankingRead)
async def get_participant_ranking(
    participant_id: int,
    service: Annotated[ParticipantRankingService, Depends(get_participant_ranking_service)],
    section_id: Annotated[
        int | None,
        Query(description="Ensure participant belongs to this section"),
    ] = None,
    jury_id: Annotated[
        int | None,
        Query(description="Ensure participant is visible to this jury member"),
    ] = None,
) -> ParticipantRankingRead:
    """Return a single leaderboard entry for the provided participant."""
    ranking = await service.get_ranking(
        participant_id,
        section_id=section_id,
        jury_id=jury_id,
    )
    if ranking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant ranking for id {participant_id} not found",
        )
    return ranking
