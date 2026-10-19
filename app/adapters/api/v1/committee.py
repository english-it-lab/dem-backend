from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.adapters.api.dependencies import get_committee_service
from app.schemas import CommitteeMemberCreate, CommitteeMemberRead
from app.services.committee import CommitteeService

router = APIRouter(tags=["committee"])


@router.get("/events/{event_id}/committee", response_model=list[CommitteeMemberRead])
async def list_committee(
    event_id: int,
    service: Annotated[CommitteeService, Depends(get_committee_service)],
) -> list[CommitteeMemberRead]:
    members = await service.list_by_event(event_id)
    return [CommitteeMemberRead.model_validate(m) for m in members]


@router.post("/events/{event_id}/committee", response_model=CommitteeMemberRead, status_code=status.HTTP_201_CREATED)
async def create_committee_member(
    event_id: int,
    payload: CommitteeMemberCreate,
    service: Annotated[CommitteeService, Depends(get_committee_service)],
) -> CommitteeMemberRead:
    if payload.event_id != event_id:
        raise HTTPException(status_code=400, detail="event_id in path must match event_id in body")
    member = await service.create(payload)
    return CommitteeMemberRead.model_validate(member)


@router.put("/events/{event_id}/committee/{member_id}", response_model=CommitteeMemberRead)
async def update_committee_member(
    event_id: int,
    member_id: int,
    payload: CommitteeMemberCreate,
    service: Annotated[CommitteeService, Depends(get_committee_service)],
) -> CommitteeMemberRead:
    if payload.event_id != event_id:
        raise HTTPException(status_code=400, detail="event_id in path must match event_id in body")
    try:
        member = await service.update(member_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return CommitteeMemberRead.model_validate(member)


@router.delete("/events/{event_id}/committee/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_committee_member(
    event_id: int,  # noqa: ARG001
    member_id: int,
    service: Annotated[CommitteeService, Depends(get_committee_service)],
) -> None:
    try:
        await service.delete(member_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
