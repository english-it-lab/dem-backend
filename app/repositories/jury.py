from collections.abc import Sequence

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Jury, JuryScore, Participant, Person, SectionJury
from app.schemas import JuryCreate, JuryUpdate


class JuryRepository:
    """Data access layer for jury members."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_juries(
        self,
        university_id: int | None = None,
        is_chairman: bool | None = None,
    ) -> Sequence[Jury]:
        stmt = select(Jury)

        if university_id is not None:
            stmt = stmt.where(Jury.university_id == university_id)
        if is_chairman is not None:
            stmt = stmt.where(Jury.is_chairman == is_chairman)

        stmt = stmt.order_by(Jury.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_jury_by_id(self, jury_id: int) -> Jury | None:
        """
        Retrieve a jury member by ID.

        Args:
            jury_id: ID of the jury member

        Returns:
            Jury instance or None if not found
        """
        stmt = select(Jury).where(Jury.id == jury_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_jury(self, data: JuryCreate) -> Jury:
        jury = Jury(
            university_id=data.university_id,
            person_id=data.person_id,
            is_chairman=data.is_chairman,
            access_key=data.access_key,
        )
        self._session.add(jury)

        await self._session.commit()
        await self._session.flush()

        return jury

    async def update_jury(self, jury: Jury, data: JuryUpdate) -> Jury:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(jury, field, value)

        await self._session.flush()
        await self._session.refresh(jury)
        return jury

    async def delete_jury(self, jury: Jury) -> None:
        await self._session.delete(jury)
        await self._session.flush()

    async def get_jury_progress(self, jury_id: int) -> Sequence[dict]:
        """
        Get list of participants for the jury's section with grading status.
        """
        subquery_sections = select(SectionJury.section_id).where(SectionJury.jury_id == jury_id).scalar_subquery()
        stmt = (
            select(
                Participant.id.label("participant_id"),
                Person.first_name,
                Person.last_name,
                Participant.presentation_topic,
                case((JuryScore.id.is_not(None), True), else_=False).label("is_graded"),
                (
                    func.coalesce(JuryScore.organization_score, 0)
                    + func.coalesce(JuryScore.content, 0)
                    + func.coalesce(JuryScore.visuals, 0)
                    + func.coalesce(JuryScore.mechanics, 0)
                    + func.coalesce(JuryScore.delivery, 0)
                ).label("current_score"),
            )
            .join(Person, Participant.person_id == Person.id)
            .outerjoin(JuryScore, and_(JuryScore.participant_id == Participant.id, JuryScore.jury_id == jury_id))
            .where(Participant.section_id.in_(subquery_sections))
            .order_by(Person.last_name)
        )

        result = await self._session.execute(stmt)
        return result.all()
