from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PosterContent
from app.schemas import PosterContentCreate, PosterContentUpdate


class PosterContentRepository:
    """Data access layer for poster content."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_poster_contents(self) -> Sequence[PosterContent]:
        """Retrieve all poster contents ordered by ID."""
        stmt = select(PosterContent).order_by(PosterContent.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_poster_content_by_id(self, content_id: int) -> PosterContent | None:
        """
        Retrieve poster content by ID.

        Args:
            content_id: ID of the poster content

        Returns:
            PosterContent instance or None if not found
        """
        stmt = select(PosterContent).where(PosterContent.id == content_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_poster_content(self, data: PosterContentCreate) -> PosterContent:
        """Create new poster content."""
        content = PosterContent(
            technical_requirements_id=data.technical_requirements_id,
            words_amount=data.words_amount,
            images_amount=data.images_amount,
        )
        self._session.add(content)
        await self._session.commit()
        await self._session.flush()
        return content

    async def update_poster_content(self, content: PosterContent, data: PosterContentUpdate) -> PosterContent:
        """
        Update existing poster content.

        Args:
            content: Existing PosterContent instance
            data: Update data with optional fields

        Returns:
            Updated PosterContent instance
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(content, field, value)

        await self._session.flush()
        await self._session.refresh(content)
        return content

    async def delete_poster_content(self, content: PosterContent) -> None:
        """Delete poster content."""
        await self._session.delete(content)
        await self._session.flush()
