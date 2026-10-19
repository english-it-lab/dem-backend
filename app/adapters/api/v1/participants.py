from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.adapters.api.dependencies import get_participant_service
from app.schemas import ParticipantCreate, ParticipantRead, ParticipantUpdate
from app.services.participant import ParticipantService

router = APIRouter(tags=["participants"])


@router.get("/", response_model=list[ParticipantRead])
async def read_participants(
    service: Annotated[ParticipantService, Depends(get_participant_service)], skip: int = 0, limit: int = 100
) -> list[ParticipantRead]:
    """Retrieve list of participants size of limit and with offset of skip."""
    participant = await service.list_participants(skip, limit)
    return [ParticipantRead.model_validate(s) for s in participant]


@router.get("/{participant_id}", response_model=ParticipantRead)
async def read_participant(
    participant_id: int, service: Annotated[ParticipantService, Depends(get_participant_service)]
) -> ParticipantRead:
    """
    Retrieve participant by ID.

    Args:

        participant_id: participant id

    Returns:

        Participant with specified id
    """
    return ParticipantRead.model_validate(await service.get_participant_by_id(participant_id))


@router.post("/", response_model=ParticipantRead, status_code=status.HTTP_201_CREATED)
async def create_participant(
    data: ParticipantCreate, service: Annotated[ParticipantService, Depends(get_participant_service)]
) -> ParticipantRead:
    """
    Create new participant.

    Args:

        data: participant data

    Returns:

        Created participant
    """
    return ParticipantRead.model_validate(await service.create_participant(data))


@router.patch("/{participant_id}", response_model=ParticipantRead)
async def update_participant(
    participant_id: int,
    data: ParticipantUpdate,
    service: Annotated[ParticipantService, Depends(get_participant_service)],
) -> ParticipantRead:
    """
    Update existing participant.

    Args:

        participant_id: participant id
        data: Update data

    Returns:

        Updated participant
    """
    return ParticipantRead.model_validate(await service.update_participant(participant_id, data))


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_participant(
    participant_id: int, service: Annotated[ParticipantService, Depends(get_participant_service)]
) -> None:
    """
    Delete participant.

    Args:

        participant_id: participant id
    """
    await service.delete_participant(participant_id)
