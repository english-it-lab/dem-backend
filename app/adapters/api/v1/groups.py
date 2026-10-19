from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.api.dependencies import get_current_user, get_group_invite_service, get_group_service
from app.models import Group
from app.schemas import GroupCreate, GroupFilter, GroupRead, GroupUpdate, InviteTokenResponse
from app.services.group import GroupService
from app.services.group_invites import GroupInviteService

router = APIRouter(tags=["groups"])


@router.get("/", response_model=list[GroupRead])
async def list_groups(
    params: Annotated[GroupFilter, Query()],
    service: Annotated[GroupService, Depends(get_group_service)],
) -> list[GroupRead]:
    groups = await service.list_groups(params)
    return [GroupRead.model_validate(group) for group in groups]


@router.get("/{group_id}", response_model=GroupRead)
async def get_group(
    group_id: int,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupRead:
    group = await service.get_group_by_id(group_id)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found",
        )

    return GroupRead.model_validate(group)


@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
    user_id: Annotated[int, Depends(get_current_user)],
    payload: GroupCreate,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupRead:
    result = await service.create_group(user_id, payload)

    match result:
        case Group() as group:
            return GroupRead.model_validate(group)

        case "INCOMPLETE_PROFILE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="There are empty fields in users profile"
            )

        case "SECTION_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Section with id {payload.section_id} not found"
            )


@router.patch("/", response_model=GroupRead)
async def update_group(
    user_id: Annotated[int, Depends(get_current_user)],
    group_id: int,
    payload: GroupUpdate,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupRead:
    result = await service.update_group(user_id, group_id, payload)

    match result:
        case "NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group with id {group_id} not found")

        case "NOT_LEADER":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only leader can submit group")

        case Group() as group:
            return GroupRead.model_validate(group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    user_id: Annotated[int, Depends(get_current_user)],
    group_id: int,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> None:
    result = await service.delete_group(user_id, group_id)

    match result:
        case "NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group with id {group_id} not found")

        case "NOT_LEADER":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only leader can submit group")

        case "GOOD":
            pass


@router.post("/{group_id}/submit")
async def submit_group(
    user_id: Annotated[int, Depends(get_current_user)],
    group_id: int,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupRead:
    result = await service.submit_group(user_id, group_id)

    match result:
        case Group() as group:
            return GroupRead.model_validate(group)

        case "NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group with id {group_id} not found")

        case "NOT_LEADER":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only leader can submit group")

        case "TRANSITION_ERROR":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Group status must be FORMING"
            )

        case "INCOMPLETE_PROFILE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="To sumbit all participants must fill their respective participant data",
            )


@router.post("/{group_id}/approve")
async def approve_group(
    user_id: Annotated[int, Depends(get_current_user)],
    group_id: int,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupRead:
    result = await service.approve_group(user_id, group_id)

    match result:
        case Group() as group:
            return GroupRead.model_validate(group)

        case "NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group with id {group_id} not found")

        case "NOT_ORGANIZER":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only organizer can approve group")

        case "TRANSITION_ERROR":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Group status must be PENDING"
            )


@router.post("/{group_id}/reject")
async def reject_group(
    user_id: Annotated[int, Depends(get_current_user)],
    group_id: int,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupRead:
    result = await service.reject_group(user_id, group_id)

    match result:
        case Group() as group:
            return GroupRead.model_validate(group)

        case "NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group with id {group_id} not found")

        case "NOT_ORGANIZER":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only organizer can reject group")

        case "TRANSITION_ERROR":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Group status must be PENDING"
            )


@router.post("/{group-id}/invite-token")
async def invite_token(
    group_id: int,
    person_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[GroupInviteService, Depends(get_group_invite_service)],
) -> InviteTokenResponse:
    return await service.create_invite_token(group_id=group_id, person_id=person_id)


@router.post("/join/{token}")
async def join_by_token(
    token: str,
    person_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[GroupInviteService, Depends(get_group_invite_service)],
) -> GroupRead:
    group = await service.join_by_token(token=token, person_id=person_id)

    if group is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="There are empty fields in users profile")

    return GroupRead.model_validate(group)
