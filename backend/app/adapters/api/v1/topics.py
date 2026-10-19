from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.adapters.api.dependencies import get_topic_service
from app.schemas import TopicCreate, TopicRead, TopicUpdate
from app.services.topic import TopicService

router = APIRouter(tags=["Topics"])

# The frontend calls both "/topics?sectionId=1" and "/topics/". Collection
# routes are registered under both spellings so neither triggers a 307 redirect;
# only the slash-less form appears in the OpenAPI schema.

SectionIdQuery = Annotated[int, Query(alias="sectionId", ge=1)]
OptionalSectionIdQuery = Annotated[int | None, Query(alias="sectionId", ge=1)]
TopicServiceDep = Annotated[TopicService, Depends(get_topic_service)]


@router.get("", response_model=list[TopicRead])
@router.get("/", response_model=list[TopicRead], include_in_schema=False)
async def list_topics(service: TopicServiceDep, section_id: OptionalSectionIdQuery = None) -> list[TopicRead]:
    """List topics, optionally filtered by section."""
    topics = await service.list_topics(section_id)
    return [TopicRead.model_validate(t) for t in topics]


@router.post("", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=TopicRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_topic(section_id: SectionIdQuery, data: TopicCreate, service: TopicServiceDep) -> TopicRead:
    """Create a topic inside a section."""
    return TopicRead.model_validate(await service.create_topic(section_id, data))


@router.get("/{topic_id}", response_model=TopicRead)
async def get_topic(topic_id: int, service: TopicServiceDep) -> TopicRead:
    return TopicRead.model_validate(await service.get_topic(topic_id))


@router.put("/{topic_id}", response_model=TopicRead)
async def update_topic(
    topic_id: int,
    data: TopicUpdate,
    service: TopicServiceDep,
    section_id: OptionalSectionIdQuery = None,
) -> TopicRead:
    """Update a topic. A `sectionId` query parameter is accepted as a fallback for `section_id` in the body."""
    if data.section_id is None and section_id is not None:
        data = data.model_copy(update={"section_id": section_id})
    return TopicRead.model_validate(await service.update_topic(topic_id, data))


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(topic_id: int, service: TopicServiceDep) -> None:
    await service.delete_topic(topic_id)
