from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TextbookLevel
from app.schemas import TextbookLevelUpdate


class TextbookLevelRepository:
    """Data access layer for textbook_level content."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_textbook_levels(self) -> Sequence[TextbookLevel]:
        """Retrieve all textbook_levels ordered by ID."""
        stmt = select(TextbookLevel).order_by(TextbookLevel.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_textbook_level_by_id(self, textbook_level_id: int) -> TextbookLevel | None:
        """
        Retrieve textbook_level by ID.

        Args:
            textbook_level_id: ID of the textbook_level

        Returns:
            TextbookLevel instance or None if not found
        """
        stmt = select(TextbookLevel).where(TextbookLevel.id == textbook_level_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_textbook_level(self, data: TextbookLevel) -> TextbookLevel:
        """Create new poster content."""
        content = TextbookLevel(level_abbreviation=data.level_abbreviation)
        self._session.add(content)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(content)
        return content

    async def update_textbook_level(self, textbook_level: TextbookLevel, data: TextbookLevelUpdate) -> TextbookLevel:
        """
        Update existing textbook_level.

        Args:
            textbook_level: Existing TextbookLevel instance
            data: Update data with optional fields

        Returns:
            Updated TextbookLevel instance
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(textbook_level, field, value)

        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(textbook_level)
        return textbook_level

    async def delete_textbook_level(self, textbook_level: TextbookLevel) -> None:
        """Delete textbook_level content."""
        await self._session.delete(textbook_level)
        await self._session.flush()
        await self._session.commit()
