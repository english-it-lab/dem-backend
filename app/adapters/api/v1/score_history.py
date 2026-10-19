from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.api.dependencies import get_score_history_service
from app.schemas import ScoreHistoryCreate, ScoreHistoryRead, ScoreHistoryUpdate
from app.services.score_history import ScoreHistoryService

router = APIRouter(tags=["score-history"])


@router.get("/", response_model=list[ScoreHistoryRead])
async def list_score_history(
    service: Annotated[ScoreHistoryService, Depends(get_score_history_service)],
    jury_scores_id: Annotated[int | None, Query()] = None,
    jury_id: Annotated[int | None, Query()] = None,
) -> list[ScoreHistoryRead]:
    history = await service.list_history(jury_scores_id=jury_scores_id, jury_id=jury_id)
    return [ScoreHistoryRead.model_validate(item) for item in history]


@router.get("/{history_id}", response_model=ScoreHistoryRead)
async def get_score_history(
    history_id: int,
    service: Annotated[ScoreHistoryService, Depends(get_score_history_service)],
) -> ScoreHistoryRead:
    history = await service.get_history_by_id(history_id)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score history entry with id {history_id} not found",
        )
    return ScoreHistoryRead.model_validate(history)


@router.post("/", response_model=ScoreHistoryRead, status_code=status.HTTP_201_CREATED)
async def create_score_history(
    payload: ScoreHistoryCreate,
    service: Annotated[ScoreHistoryService, Depends(get_score_history_service)],
) -> ScoreHistoryRead:
    history = await service.create_history(payload)
    return ScoreHistoryRead.model_validate(history)


@router.patch("/{history_id}", response_model=ScoreHistoryRead)
async def update_score_history(
    history_id: int,
    payload: ScoreHistoryUpdate,
    service: Annotated[ScoreHistoryService, Depends(get_score_history_service)],
) -> ScoreHistoryRead:
    history = await service.update_history(history_id, payload)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score history entry with id {history_id} not found",
        )
    return ScoreHistoryRead.model_validate(history)


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_score_history(
    history_id: int,
    service: Annotated[ScoreHistoryService, Depends(get_score_history_service)],
) -> None:
    deleted = await service.delete_history(history_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score history entry with id {history_id} not found",
        )
