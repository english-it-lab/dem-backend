from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.api.dependencies import get_technical_requirement_service
from app.schemas import (
    TechnicalRequirementCreate,
    TechnicalRequirementRead,
    TechnicalRequirementReadWithContent,
    TechnicalRequirementUpdate,
)
from app.services.technical_requirement import TechnicalRequirementService

router = APIRouter(tags=["technical-requirements"])


@router.get("/", response_model=list[TechnicalRequirementRead])
async def list_technical_requirements(
    service: Annotated[TechnicalRequirementService, Depends(get_technical_requirement_service)],
) -> list[TechnicalRequirementRead]:
    """Retrieve all technical requirements."""
    requirements = await service.list_technical_requirements()
    return [TechnicalRequirementRead.model_validate(req) for req in requirements]


@router.get("/{requirement_id}", response_model=TechnicalRequirementReadWithContent)
async def get_technical_requirement(
    requirement_id: int,
    service: Annotated[TechnicalRequirementService, Depends(get_technical_requirement_service)],
    include_content: bool = Query(default=True, description="Include related poster content"),
) -> TechnicalRequirementReadWithContent:
    """
    Retrieve a technical requirement by ID.

    Args:
        requirement_id: ID of the technical requirement
        include_content: Whether to include related poster content (default: True)

    Returns:
        Technical requirement with optional poster content

    Raises:
        HTTPException: 404 if technical requirement not found
    """  # noqa: E501
    requirement = await service.get_technical_requirement_by_id(requirement_id, with_content=include_content)
    if requirement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical requirement with id {requirement_id} not found",
        )
    return TechnicalRequirementReadWithContent.model_validate(requirement)


@router.post(
    "/",
    response_model=TechnicalRequirementRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_technical_requirement(
    payload: TechnicalRequirementCreate,
    service: Annotated[TechnicalRequirementService, Depends(get_technical_requirement_service)],
) -> TechnicalRequirementRead:
    """
    Create a new technical requirement.

    Args:
        payload: Technical requirement data

    Returns:
        Created technical requirement
    """
    requirement = await service.create_technical_requirement(payload)
    return TechnicalRequirementRead.model_validate(requirement)


@router.patch("/{requirement_id}", response_model=TechnicalRequirementRead)
async def update_technical_requirement(
    requirement_id: int,
    payload: TechnicalRequirementUpdate,
    service: Annotated[TechnicalRequirementService, Depends(get_technical_requirement_service)],
) -> TechnicalRequirementRead:
    """
    Update an existing technical requirement.

    Args:
        requirement_id: ID of the technical requirement to update
        payload: Update data (all fields optional)

    Returns:
        Updated technical requirement

    Raises:
        HTTPException: 404 if technical requirement not found
    """
    requirement = await service.update_technical_requirement(requirement_id, payload)
    if requirement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical requirement with id {requirement_id} not found",
        )
    return TechnicalRequirementRead.model_validate(requirement)


@router.delete("/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_technical_requirement(
    requirement_id: int,
    service: Annotated[TechnicalRequirementService, Depends(get_technical_requirement_service)],
) -> None:
    """
    Delete a technical requirement.

    Args:
        requirement_id: ID of the technical requirement to delete

    Raises:
        HTTPException: 404 if technical requirement not found
    """
    deleted = await service.delete_technical_requirement(requirement_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical requirement with id {requirement_id} not found",
        )
