from collections.abc import Sequence

from app.models import CommitteeMember
from app.repositories.committee_member import CommitteeMemberRepository
from app.schemas import CommitteeMemberCreate


class CommitteeService:
    """Business logic for committee members."""

    def __init__(self, repository: CommitteeMemberRepository) -> None:
        self._repository = repository

    async def list_by_event(self, event_id: int) -> Sequence[CommitteeMember]:
        return await self._repository.list_by_event(event_id)

    async def get_by_id(self, member_id: int) -> CommitteeMember | None:
        return await self._repository.get_by_id(member_id)

    async def create(self, payload: CommitteeMemberCreate) -> CommitteeMember:
        return await self._repository.create(payload)

    async def update(self, member_id: int, payload: CommitteeMemberCreate) -> CommitteeMember:
        member = await self._repository.get_by_id(member_id)
        if not member:
            raise ValueError(f"Член оргкомитета {member_id} не найден")
        return await self._repository.update(member, payload)

    async def delete(self, member_id: int) -> None:
        member = await self._repository.get_by_id(member_id)
        if not member:
            raise ValueError(f"Член оргкомитета {member_id} не найден")
        await self._repository.delete(member)
