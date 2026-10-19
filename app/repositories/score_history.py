from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import JuryScoreChange
from app.schemas import ScoreHistoryCreate, ScoreHistoryUpdate


class ScoreHistoryRepository:
    """Data access layer for jury score change history."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_history(
        self,
        *,
        jury_scores_id: int | None = None,
        jury_id: int | None = None,
    ) -> Sequence[JuryScoreChange]:
        stmt = select(JuryScoreChange).order_by(JuryScoreChange.update_time.desc(), JuryScoreChange.id.desc())

        if jury_scores_id is not None:
            stmt = stmt.where(JuryScoreChange.jury_scores_id == jury_scores_id)
        if jury_id is not None:
            stmt = stmt.where(JuryScoreChange.jury_id == jury_id)

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_history_by_id(self, history_id: int) -> JuryScoreChange | None:
        stmt = select(JuryScoreChange).where(JuryScoreChange.id == history_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_history(self, payload: ScoreHistoryCreate) -> JuryScoreChange:
        history = JuryScoreChange(
            jury_scores_id=payload.jury_scores_id,
            jury_id=payload.jury_id,
            update_time=payload.update_time,
        )
        self._session.add(history)
        await self._session.flush()
        await self._session.refresh(history)
        return history

    async def update_history(self, history: JuryScoreChange, payload: ScoreHistoryUpdate) -> JuryScoreChange:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(history, field, value)

        await self._session.flush()
        await self._session.refresh(history)
        return history

    async def delete_history(self, history: JuryScoreChange) -> None:
        await self._session.delete(history)
        await self._session.flush()
