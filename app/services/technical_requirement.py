from collections.abc import Sequence

from fastapi import HTTPException, status

from app.models import TechnicalRequirement
from app.repositories.technical_requirement import (
    TechnicalRequirementRepository,
)
from app.repositories.topic import TopicRepository
from app.schemas import TechnicalRequirementCreate, TechnicalRequirementUpdate


class TechnicalRequirementService:
    """Business logic for technical requirement entities."""

    def __init__(
        self,
        repository: TechnicalRequirementRepository,
        topic_repository: TopicRepository,
    ) -> None:
        self._repository = repository
        self._topic_repository = topic_repository

    async def list_technical_requirements(
        self,
    ) -> Sequence[TechnicalRequirement]:
        """Retrieve all technical requirements."""
        return await self._repository.list_technical_requirements()

    async def get_technical_requirement_by_id(
        self, requirement_id: int, with_content: bool = False
    ) -> TechnicalRequirement | None:
        """
        Retrieve a technical requirement by ID.

        Args:
            requirement_id: ID of the technical requirement
            with_content: If True, include related poster content

        Returns:
            TechnicalRequirement instance or None if not found
        """
        return await self._repository.get_technical_requirement_by_id(requirement_id, with_content=with_content)

    async def create_technical_requirement(self, payload: TechnicalRequirementCreate) -> TechnicalRequirement:
        """Create a new technical requirement."""
        if payload.topic_id is not None:
            topic = await self._topic_repository.get_topic_by_id(payload.topic_id)
            if topic is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Topic with id {payload.topic_id} not found",
                )

        return await self._repository.create_technical_requirement(payload)

    async def update_technical_requirement(
        self, requirement_id: int, payload: TechnicalRequirementUpdate
    ) -> TechnicalRequirement | None:
        """
        Update an existing technical requirement.

        Args:
            requirement_id: ID of the technical requirement to update
            payload: Update data

        Returns:
            Updated TechnicalRequirement or None if not found
        """
        requirement = await self._repository.get_technical_requirement_by_id(requirement_id)
        if requirement is None:
            return None

        if payload.topic_id is not None:
            topic = await self._topic_repository.get_topic_by_id(payload.topic_id)
            if topic is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Topic with id {payload.topic_id} not found",
                )

        return await self._repository.update_technical_requirement(requirement, payload)

    async def delete_technical_requirement(self, requirement_id: int) -> bool:
        """
        Delete a technical requirement.

        Args:
            requirement_id: ID of the technical requirement to delete

        Returns:
            True if deleted, False if not found
        """
        requirement = await self._repository.get_technical_requirement_by_id(requirement_id)
        if requirement is None:
            return False

        await self._repository.delete_technical_requirement(requirement)
        return True
