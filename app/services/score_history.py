from collections.abc import Sequence

from fastapi import HTTPException, status

from app.models import JuryScoreChange
from app.repositories.jury import JuryRepository
from app.repositories.jury_score import JuryScoreRepository
from app.repositories.score_history import ScoreHistoryRepository
from app.schemas import ScoreHistoryCreate, ScoreHistoryUpdate


class ScoreHistoryService:
    """Business logic for jury score change history."""

    def __init__(
        self,
        score_history_repository: ScoreHistoryRepository,
        jury_score_repository: JuryScoreRepository,
        jury_repository: JuryRepository,
    ) -> None:
        self._repository = score_history_repository
        self._jury_score_repository = jury_score_repository
        self._jury_repository = jury_repository

    async def list_history(
        self,
        *,
        jury_scores_id: int | None = None,
        jury_id: int | None = None,
    ) -> Sequence[JuryScoreChange]:
        return await self._repository.list_history(jury_scores_id=jury_scores_id, jury_id=jury_id)

    async def get_history_by_id(self, history_id: int) -> JuryScoreChange | None:
        return await self._repository.get_history_by_id(history_id)

    async def create_history(self, payload: ScoreHistoryCreate) -> JuryScoreChange:
        await self._validate_jury_score_exists(payload.jury_scores_id)
        if payload.jury_id is not None:
            await self._validate_jury_exists(payload.jury_id)

        return await self._repository.create_history(payload)

    async def update_history(self, history_id: int, payload: ScoreHistoryUpdate) -> JuryScoreChange | None:
        history = await self._repository.get_history_by_id(history_id)
        if history is None:
            return None

        if payload.jury_scores_id is not None:
            await self._validate_jury_score_exists(payload.jury_scores_id)
        if payload.jury_id is not None:
            await self._validate_jury_exists(payload.jury_id)

        return await self._repository.update_history(history, payload)

    async def delete_history(self, history_id: int) -> bool:
        history = await self._repository.get_history_by_id(history_id)
        if history is None:
            return False

        await self._repository.delete_history(history)
        return True

    async def _validate_jury_score_exists(self, jury_score_id: int) -> None:
        score = await self._jury_score_repository.get_score_by_id(jury_score_id)
        if score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Jury score with id {jury_score_id} not found",
            )

    async def _validate_jury_exists(self, jury_id: int) -> None:
        jury = await self._jury_repository.get_jury_by_id(jury_id)
        if jury is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Jury member with id {jury_id} not found",
            )
