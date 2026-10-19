from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Teacher
from app.schemas import TeacherUpdate


class TeacherRepository:
    """Data access layer for teacher content."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_teachers(self) -> Sequence[Teacher]:
        """Retrieve all teachers ordered by ID."""
        stmt = select(Teacher).order_by(Teacher.id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_teacher_by_id(self, teacher_id: int) -> Teacher | None:
        """
        Retrieve teacher by ID.

        Args:
            teacher_id: ID of the teacher

        Returns:
            Teacher instance or None if not found
        """
        stmt = select(Teacher).where(Teacher.id == teacher_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_teacher(self, data: Teacher) -> Teacher:
        """Create new poster content."""
        content = Teacher(university_id=data.university_id, department=data.department, person_id=data.person_id)
        self._session.add(content)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(content)
        return content

    async def update_teacher(self, teacher: Teacher, data: TeacherUpdate) -> Teacher:
        """
        Update existing teacher.

        Args:
            teacher: Existing Teacher instance
            data: Update data with optional fields

        Returns:
            Updated Teacher instance
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(teacher, field, value)

        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(teacher)
        return teacher

    async def delete_teacher(self, teacher: Teacher) -> None:
        """Delete teacher content."""
        await self._session.delete(teacher)
        await self._session.flush()
        await self._session.commit()
