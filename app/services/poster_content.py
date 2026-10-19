from collections.abc import Sequence

from fastapi import HTTPException, status

from app.models import PosterContent
from app.repositories.poster_content import PosterContentRepository
from app.repositories.technical_requirement import (
    TechnicalRequirementRepository,
)
from app.schemas import PosterContentCreate, PosterContentUpdate


class PosterContentService:
    """Business logic for poster content entities."""

    def __init__(
        self,
        repository: PosterContentRepository,
        tech_req_repository: TechnicalRequirementRepository,
    ) -> None:
        self._repository = repository
        self._tech_req_repository = tech_req_repository

    async def list_poster_contents(self) -> Sequence[PosterContent]:
        """Retrieve all poster contents."""
        return await self._repository.list_poster_contents()

    async def get_poster_content_by_id(self, content_id: int) -> PosterContent | None:
        """
        Retrieve poster content by ID.

        Args:
            content_id: ID of the poster content

        Returns:
            PosterContent instance or None if not found
        """
        return await self._repository.get_poster_content_by_id(content_id)

    async def create_poster_content(self, payload: PosterContentCreate) -> PosterContent:
        """Create new poster content."""
        if payload.technical_requirements_id is not None:
            tech_req = await self._tech_req_repository.get_technical_requirement_by_id(  # noqa: E501
                payload.technical_requirements_id
            )
            if tech_req is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Technical requirement with id {payload.technical_requirements_id} not found",  # noqa: E501
                )

        return await self._repository.create_poster_content(payload)

    async def update_poster_content(self, content_id: int, payload: PosterContentUpdate) -> PosterContent | None:
        """
        Update existing poster content.

        Args:
            content_id: ID of the poster content to update
            payload: Update data

        Returns:
            Updated PosterContent or None if not found
        """
        content = await self._repository.get_poster_content_by_id(content_id)
        if content is None:
            return None

        if payload.technical_requirements_id is not None:
            tech_req = await self._tech_req_repository.get_technical_requirement_by_id(  # noqa: E501
                payload.technical_requirements_id
            )
            if tech_req is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Technical requirement with id {payload.technical_requirements_id} not found",  # noqa: E501
                )

        return await self._repository.update_poster_content(content, payload)

    async def delete_poster_content(self, content_id: int) -> bool:
        """
        Delete poster content.

        Args:
            content_id: ID of the poster content to delete

        Returns:
            True if deleted, False if not found
        """
        content = await self._repository.get_poster_content_by_id(content_id)
        if content is None:
            return False

        await self._repository.delete_poster_content(content)
        return True
