from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.adapters.api.dependencies import get_section_service
from app.schemas import SectionCreate, SectionRead, SectionUpdate
from app.services.section import SectionService

router = APIRouter(tags=["Sections"])


@router.get("/", response_model=list[SectionRead])
async def read_sections(
    service: Annotated[SectionService, Depends(get_section_service)], skip: int = 0, limit: int = 100
) -> list[SectionRead]:
    """Retrieve list of sections size of limit and with offset of skip."""
    sections = await service.list_sections(skip, limit)
    return [SectionRead.model_validate(s) for s in sections]


@router.get("/{section_id}", response_model=SectionRead)
async def read_section(
    section_id: int, service: Annotated[SectionService, Depends(get_section_service)]
) -> SectionRead:
    """
    Retrieve section by ID.

    Args:
        section_id: section id

    Returns:
        Section with specified id
    """
    return SectionRead.model_validate(await service.get_section_by_id(section_id))


@router.post("/", response_model=SectionRead, status_code=status.HTTP_201_CREATED)
async def create_section(
    data: SectionCreate, service: Annotated[SectionService, Depends(get_section_service)]
) -> SectionRead:
    """
    Create new section.

    Args:
        data: section data

    Returns:
        Created section
    """
    return SectionRead.model_validate(await service.create_section(data))


@router.patch("/{section_id}", response_model=SectionRead)
async def update_section(
    section_id: int, data: SectionUpdate, service: Annotated[SectionService, Depends(get_section_service)]
) -> SectionRead:
    """
    Update exiting section.

    Args:
        section_id: section id
        data: Update data

    Returns:
        Updated section
    """
    return SectionRead.model_validate(await service.update_section(section_id, data))


@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(section_id: int, service: Annotated[SectionService, Depends(get_section_service)]) -> None:
    """
    Delete section.

    Args:
        section_id: section id
    """
    await service.delete_section(section_id)
