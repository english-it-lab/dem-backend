from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course
from app.schemas import CourseUpdate


class CourseRepository:
    """Data access layer for course content."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_courses(self) -> Sequence[Course]:
        """Retrieve all courses ordered by ID."""
        stmt = select(Course).order_by(Course.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_course_by_id(self, course_id: int) -> Course | None:
        """
        Retrieve course by ID.

        Args:
            course_id: ID of the course

        Returns:
            Course instance or None if not found
        """
        stmt = select(Course).where(Course.id == course_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_course(self, data: Course) -> Course:
        """Create new poster content."""
        content = Course(year=data.year)
        self._session.add(content)
        await self._session.flush()
        await self._session.refresh(content)
        return content

    async def update_course(self, course: Course, data: CourseUpdate) -> Course:
        """
        Update existing course.

        Args:
            course: Existing Course instance
            data: Update data with optional fields

        Returns:
            Updated Course instance
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        await self._session.flush()
        await self._session.refresh(course)
        return course

    async def delete_course(self, course: Course) -> None:
        """Delete course content."""
        await self._session.delete(course)
        await self._session.flush()
