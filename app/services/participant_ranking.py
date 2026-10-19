from __future__ import annotations

from math import ceil

from app.repositories.participant_ranking import (
    ParticipantRankingRecord,
    ParticipantRankingRepository,
)
from app.schemas import (
    ParticipantRankingList,
    ParticipantRankingRead,
    ParticipantRankingSortField,
    SortOrder,
)


class ParticipantRankingService:
    """Business logic wrapper around leaderboard aggregation."""

    def __init__(self, repository: ParticipantRankingRepository) -> None:
        self._repository = repository

    async def list_rankings(
        self,
        *,
        section_id: int | None,
        jury_id: int | None,
        page: int,
        page_size: int,
        sort_by: ParticipantRankingSortField,
        sort_order: SortOrder,
    ) -> ParticipantRankingList:
        rows, total = await self._repository.list_rankings(
            section_id=section_id,
            jury_id=jury_id,
            page=page,
            page_size=page_size,
            participant_id=None,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        items = [self._to_schema(row) for row in rows]
        pages = ceil(total / page_size) if page_size else 0

        return ParticipantRankingList(
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            has_next=page < pages,
            has_previous=page > 1 and total > 0,
            items=items,
        )

    async def get_ranking(
        self,
        participant_id: int,
        *,
        section_id: int | None,
        jury_id: int | None,
    ) -> ParticipantRankingRead | None:
        record = await self._repository.get_ranking_by_participant(
            participant_id,
            section_id=section_id,
            jury_id=jury_id,
        )
        if record is None:
            return None
        return self._to_schema(record)

    @staticmethod
    def _to_schema(record: ParticipantRankingRecord) -> ParticipantRankingRead:
        return ParticipantRankingRead(
            participant_id=record.participant_id,
            person_id=record.person_id,
            first_name=record.first_name,
            last_name=record.last_name,
            middle_name=record.middle_name,
            section_id=record.section_id,
            section_name=record.section_name,
            presentation_topic=record.presentation_topic,
            total_score=round(record.total_score, 2),
            scores_count=record.scores_count,
            rank=record.rank,
        )
