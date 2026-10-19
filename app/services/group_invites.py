from datetime import datetime, timedelta

from fastapi import HTTPException, status

from app.core.config import settings
from app.enums.group import GroupStatus
from app.models import Group
from app.repositories.group import GroupRepository
from app.repositories.group_participant import GroupParticipantRepository
from app.repositories.participant import ParticipantRepository
from app.repositories.person import PersonRepository
from app.schemas import InviteTokenResponse
from app.services.jwt import JwtService


class GroupInviteService:
    GROUP_ID_KEY = "group_id"

    def __init__(
        self,
        jwt_service: JwtService,
        group_repository: GroupRepository,
        participant_repository: ParticipantRepository,
        group_participant_repository: GroupParticipantRepository,
        person_repository: PersonRepository,
    ) -> None:
        self._jwt_service = jwt_service
        self._group_repository = group_repository
        self._participant_repository = participant_repository
        self._group_participant_repository = group_participant_repository
        self._person_repository = person_repository

    async def create_invite_token(self, group_id: int, person_id: int) -> InviteTokenResponse:
        if not await self._group_repository.is_leader(group_id, person_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        participant = await self._group_participant_repository.get_participant_by_group_and_person(
            group_id=group_id, person_id=person_id
        )
        if participant is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        if not participant.is_group_leader:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        payload = {self.GROUP_ID_KEY: group_id}
        token = self._jwt_service.create_jwt(payload, settings.jwt_ttl_minutes)
        return InviteTokenResponse(
            token=token, expired_at=datetime.now() + timedelta(minutes=settings.jwt_ttl_minutes)
        )

    async def join_by_token(self, token: str, person_id: int) -> Group | None:
        person = await self._person_repository.get_person_by_id(person_id)

        if not person.is_profile_complete:
            return None

        payload = self._jwt_service.decode_jwt(token)
        group_id = payload.get(self.GROUP_ID_KEY)

        if await self.is_participant_exists(group_id=group_id, person_id=person_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        group = await self._group_repository.get_group_by_id(group_id)

        if group.status != GroupStatus.FORMING:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Group already formed")

        participant = await self._participant_repository.create_participant(
            person_id=person_id, section_id=group.section_id, is_group_leader=False
        )
        await self._group_participant_repository.create_group_participant(group.id, participant.id)
        group = await self._group_repository.increment_count(group)

        return group

    async def is_participant_exists(self, group_id: int, person_id: int) -> bool:
        participant = await self._group_participant_repository.get_participant_by_group_and_person(
            group_id=group_id, person_id=person_id
        )
        return participant is not None
