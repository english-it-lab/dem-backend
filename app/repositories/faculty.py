from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Faculty
from app.schemas import FacultyUpdate


class FacultyRepository:
    """Data access layer for faculty content."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_faculties(self) -> Sequence[Faculty]:
        """Retrieve all faculties ordered by ID."""
        stmt = select(Faculty).order_by(Faculty.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_faculty_by_id(self, faculty_id: int) -> Faculty | None:
        """
        Retrieve faculty by ID.

        Args:
            faculty_id: ID of the faculty

        Returns:
            Faculty instance or None if not found
        """
        stmt = select(Faculty).where(Faculty.id == faculty_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_faculty(self, data: Faculty) -> Faculty:
        """Create new poster content."""
        content = Faculty(university_id=data.university_id, name=data.name)
        self._session.add(content)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(content)
        return content

    async def update_faculty(self, faculty: Faculty, data: FacultyUpdate) -> Faculty:
        """
        Update existing faculty.

        Args:
            faculty: Existing Faculty instance
            data: Update data with optional fields

        Returns:
            Updated Faculty instance
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(faculty, field, value)

        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(faculty)
        return faculty

    async def delete_faculty(self, faculty: Faculty) -> None:
        """Delete faculty content."""
        await self._session.delete(faculty)
        await self._session.flush()
        await self._session.commit()
