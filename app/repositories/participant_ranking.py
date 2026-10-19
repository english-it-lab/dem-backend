from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import JuryScore, Participant, Person, Section, SectionJury
from app.schemas import ParticipantRankingSortField, SortOrder


@dataclass(slots=True)
class ParticipantRankingRecord:
    """Lightweight container for aggregated leaderboard data."""

    participant_id: int
    person_id: int | None
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    section_id: int | None
    section_name: str | None
    presentation_topic: str | None
    total_score: float
    scores_count: int
    rank: int


class ParticipantRankingRepository:
    """Aggregated read-model for participant leaderboard."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_rankings(
        self,
        *,
        section_id: int | None = None,
        jury_id: int | None = None,
        participant_id: int | None = None,
        page: int,
        page_size: int,
        sort_by: ParticipantRankingSortField,
        sort_order: SortOrder,
    ) -> tuple[list[ParticipantRankingRecord], int]:
        """
        Return aggregated scores for participants ordered by the requested sorting strategy.
        """

        base_stmt = self._build_base_statement(section_id=section_id, jury_id=jury_id, participant_id=participant_id)
        leaderboard_subquery = base_stmt.subquery()
        ranked_subquery = select(
            leaderboard_subquery,
            func.dense_rank().over(order_by=leaderboard_subquery.c.total_score.desc()).label("rank"),
        ).subquery()

        stmt = select(ranked_subquery)
        stmt = self._apply_sorting(stmt, ranked_subquery, sort_by=sort_by, sort_order=sort_order)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        total_stmt = select(func.count()).select_from(leaderboard_subquery)

        result = await self._session.execute(stmt)
        rows: Sequence[dict] = result.mappings().all()
        total_result = await self._session.execute(total_stmt)
        total = int(total_result.scalar_one())

        return [self._map_row(row) for row in rows], total

    async def get_ranking_by_participant(
        self,
        participant_id: int,
        *,
        section_id: int | None = None,
        jury_id: int | None = None,
    ) -> ParticipantRankingRecord | None:
        rankings, _ = await self.list_rankings(
            section_id=section_id,
            jury_id=jury_id,
            participant_id=participant_id,
            page=1,
            page_size=1,
            sort_by=ParticipantRankingSortField.TOTAL_SCORE,
            sort_order=SortOrder.DESC,
        )
        return rankings[0] if rankings else None

    def _build_base_statement(
        self,
        *,
        section_id: int | None,
        jury_id: int | None,
        participant_id: int | None,
    ) -> Select:
        score_total = (
            func.coalesce(JuryScore.organization_score, 0.0)
            + func.coalesce(JuryScore.content, 0.0)
            + func.coalesce(JuryScore.visuals, 0.0)
            + func.coalesce(JuryScore.mechanics, 0.0)
            + func.coalesce(JuryScore.delivery, 0.0)
        )

        stmt = (
            select(
                Participant.id.label("participant_id"),
                Participant.person_id.label("person_id"),
                Person.first_name.label("first_name"),
                Person.last_name.label("last_name"),
                Person.middle_name.label("middle_name"),
                Participant.section_id.label("section_id"),
                Section.name.label("section_name"),
                Participant.presentation_topic.label("presentation_topic"),
                func.coalesce(func.sum(score_total), 0.0).label("total_score"),
                func.count(JuryScore.id).label("scores_count"),
            )
            .select_from(Participant)
            .join(Person, Participant.person_id == Person.id, isouter=True)
            .join(Section, Participant.section_id == Section.id, isouter=True)
            .outerjoin(JuryScore, JuryScore.participant_id == Participant.id)
        )

        if participant_id is not None:
            stmt = stmt.where(Participant.id == participant_id)

        if section_id is not None:
            stmt = stmt.where(Participant.section_id == section_id)

        if jury_id is not None:
            stmt = stmt.join(SectionJury, SectionJury.section_id == Participant.section_id).where(
                SectionJury.jury_id == jury_id
            )

        stmt = stmt.group_by(
            Participant.id,
            Participant.person_id,
            Person.first_name,
            Person.last_name,
            Person.middle_name,
            Participant.section_id,
            Section.name,
            Participant.presentation_topic,
        )

        return stmt

    def _apply_sorting(
        self,
        stmt: Select,
        ranked_subquery,
        *,
        sort_by: ParticipantRankingSortField,
        sort_order: SortOrder,
    ) -> Select:
        column_map = {
            ParticipantRankingSortField.TOTAL_SCORE: ranked_subquery.c.total_score,
            ParticipantRankingSortField.LAST_NAME: ranked_subquery.c.last_name,
            ParticipantRankingSortField.FIRST_NAME: ranked_subquery.c.first_name,
            ParticipantRankingSortField.RANK: ranked_subquery.c.rank,
            ParticipantRankingSortField.SCORES_COUNT: ranked_subquery.c.scores_count,
        }

        primary_column = column_map.get(sort_by)
        if primary_column is None:
            primary_column = ranked_subquery.c.total_score

        primary_order = primary_column.desc() if sort_order == SortOrder.DESC else primary_column.asc()

        order_clauses = [primary_order]

        # Ensure a deterministic order for ties to satisfy the alphabetical requirement.
        order_clauses.append(ranked_subquery.c.total_score.desc())
        order_clauses.append(ranked_subquery.c.last_name.asc().nullslast())
        order_clauses.append(ranked_subquery.c.first_name.asc().nullslast())

        return stmt.order_by(*order_clauses)

    @staticmethod
    def _map_row(row: dict) -> ParticipantRankingRecord:
        record = ParticipantRankingRecord(
            participant_id=row["participant_id"],
            person_id=row.get("person_id"),
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            middle_name=row.get("middle_name"),
            section_id=row.get("section_id"),
            section_name=row.get("section_name"),
            presentation_topic=row.get("presentation_topic"),
            total_score=float(row.get("total_score") or 0.0),
            scores_count=int(row.get("scores_count") or 0),
            rank=int(row.get("rank") or 0),
        )
        return record
