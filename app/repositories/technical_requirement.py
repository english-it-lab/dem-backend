from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import TechnicalRequirement
from app.schemas import TechnicalRequirementCreate, TechnicalRequirementUpdate


class TechnicalRequirementRepository:
    """Data access layer for technical requirements."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_technical_requirements(
        self,
    ) -> Sequence[TechnicalRequirement]:
        """Retrieve all technical requirements ordered by ID."""
        stmt = select(TechnicalRequirement).order_by(TechnicalRequirement.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_technical_requirement_by_id(
        self, requirement_id: int, with_content: bool = False
    ) -> TechnicalRequirement | None:
        """
        Retrieve a technical requirement by ID.

        Args:
            requirement_id: ID of the technical requirement
            with_content: If True, eagerly load related poster content

        Returns:
            TechnicalRequirement instance or None if not found
        """
        stmt = select(TechnicalRequirement).where(TechnicalRequirement.id == requirement_id)

        if with_content:
            # Eager loading using selectinload to avoid N+1 queries
            stmt = stmt.options(selectinload(TechnicalRequirement.posters_content))

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_technical_requirement(self, data: TechnicalRequirementCreate) -> TechnicalRequirement:
        """Create a new technical requirement."""
        requirement = TechnicalRequirement(
            topic_id=data.topic_id,
            format=data.format,
            sizes=data.sizes,
        )
        self._session.add(requirement)
        await self._session.commit()
        await self._session.flush()
        return requirement

    async def update_technical_requirement(
        self,
        requirement: TechnicalRequirement,
        data: TechnicalRequirementUpdate,
    ) -> TechnicalRequirement:
        """
        Update an existing technical requirement.

        Args:
            requirement: Existing TechnicalRequirement instance
            data: Update data with optional fields

        Returns:
            Updated TechnicalRequirement instance
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(requirement, field, value)

        await self._session.flush()
        await self._session.refresh(requirement)
        return requirement

    async def delete_technical_requirement(self, requirement: TechnicalRequirement) -> None:
        """Delete a technical requirement."""
        await self._session.delete(requirement)
        await self._session.flush()
