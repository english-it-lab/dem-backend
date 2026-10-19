from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.adapters.api.dependencies import get_poster_content_service
from app.schemas import (
    PosterContentCreate,
    PosterContentRead,
    PosterContentUpdate,
)
from app.services.poster_content import PosterContentService

router = APIRouter(tags=["poster-contents"])


@router.get("/", response_model=list[PosterContentRead])
async def list_poster_contents(
    service: Annotated[PosterContentService, Depends(get_poster_content_service)],
) -> list[PosterContentRead]:
    """Retrieve all poster contents."""
    contents = await service.list_poster_contents()
    return [PosterContentRead.model_validate(content) for content in contents]


@router.get("/{content_id}", response_model=PosterContentRead)
async def get_poster_content(
    content_id: int,
    service: Annotated[PosterContentService, Depends(get_poster_content_service)],
) -> PosterContentRead:
    """
    Retrieve poster content by ID.

    Args:
        content_id: ID of the poster content

    Returns:
        Poster content

    Raises:
        HTTPException: 404 if poster content not found
    """
    content = await service.get_poster_content_by_id(content_id)
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Poster content with id {content_id} not found",
        )
    return PosterContentRead.model_validate(content)


@router.post("/", response_model=PosterContentRead, status_code=status.HTTP_201_CREATED)
async def create_poster_content(
    payload: PosterContentCreate,
    service: Annotated[PosterContentService, Depends(get_poster_content_service)],
) -> PosterContentRead:
    """
    Create new poster content.

    Args:
        payload: Poster content data

    Returns:
        Created poster content
    """
    content = await service.create_poster_content(payload)
    return PosterContentRead.model_validate(content)


@router.patch("/{content_id}", response_model=PosterContentRead)
async def update_poster_content(
    content_id: int,
    payload: PosterContentUpdate,
    service: Annotated[PosterContentService, Depends(get_poster_content_service)],
) -> PosterContentRead:
    """
    Update existing poster content.

    Args:
        content_id: ID of the poster content to update
        payload: Update data (all fields optional)

    Returns:
        Updated poster content

    Raises:
        HTTPException: 404 if poster content not found
    """
    content = await service.update_poster_content(content_id, payload)
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Poster content with id {content_id} not found",
        )
    return PosterContentRead.model_validate(content)


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_poster_content(
    content_id: int,
    service: Annotated[PosterContentService, Depends(get_poster_content_service)],
) -> None:
    """
    Delete poster content.

    Args:
        content_id: ID of the poster content to delete

    Raises:
        HTTPException: 404 if poster content not found
    """
    deleted = await service.delete_poster_content(content_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Poster content with id {content_id} not found",
        )
