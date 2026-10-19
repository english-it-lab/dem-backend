import logging
import random

from fastapi import HTTPException, status

from app.repositories.group import GroupRepository
from app.repositories.group_topic import GroupTopicRepository
from app.repositories.section import SectionRepository
from app.repositories.topic import TopicRepository
from app.schemas import DrawGroupRead, DrawResultRead, DrawRunResult, DrawTopicRead, GroupFilter

logger = logging.getLogger(__name__)


class DrawService:
    """Randomly distributes a section's topics between its groups."""

    def __init__(
        self,
        topic_repo: TopicRepository,
        group_repo: GroupRepository,
        group_topic_repo: GroupTopicRepository,
        section_repo: SectionRepository,
    ) -> None:
        self.topic_repo = topic_repo
        self.group_repo = group_repo
        self.group_topic_repo = group_topic_repo
        self.section_repo = section_repo

    async def run_draw(self, section_id: int) -> DrawRunResult:
        """Run the draw for a section, replacing any previous assignment."""
        await self._ensure_section_exists(section_id)
        topics = list(await self.topic_repo.list_topics(section_id))
        groups = list(await self.group_repo.list_groups(GroupFilter(section_id=section_id)))

        if not topics:
            raise HTTPException(status.HTTP_409_CONFLICT, "Нет тем для распределения в секции")
        if not groups:
            raise HTTPException(status.HTTP_409_CONFLICT, "Нет групп для распределения в секции")

        shuffled = random.sample(topics, len(topics))
        # Distribute as evenly as possible; the first `remainder` groups get one extra topic.
        base, remainder = divmod(len(shuffled), len(groups))

        results: list[DrawResultRead] = []
        empty_groups: list[DrawGroupRead] = []
        topic_idx = 0
        for i, group in enumerate(groups):
            count = base + (1 if i < remainder else 0)
            assigned = shuffled[topic_idx : topic_idx + count]
            topic_idx += count
            results.append(
                DrawResultRead(
                    group_id=group.id,
                    group_name=group.name,
                    topics=[DrawTopicRead(topic_id=t.id, topic_name=t.name) for t in assigned],
                )
            )
            if not assigned:
                empty_groups.append(DrawGroupRead(group_id=group.id, group_name=group.name))

        await self.group_topic_repo.clear_section(section_id)
        for result in results:
            for topic in result.topics:
                await self.group_topic_repo.create(result.group_id, topic.topic_id)

        if empty_groups:
            logger.warning("Section %s: groups without topics: %s", section_id, [g.group_name for g in empty_groups])

        return DrawRunResult(
            section_id=section_id,
            results=results,
            empty_groups=empty_groups,
            total_topics=len(topics),
            total_groups=len(groups),
        )

    async def get_results(self, section_id: int) -> list[DrawResultRead]:
        """Return the persisted draw for a section; groups without topics are included with an empty list."""
        await self._ensure_section_exists(section_id)
        groups = await self.group_repo.list_groups(GroupFilter(section_id=section_id))
        rows = await self.group_topic_repo.get_by_section(section_id)

        topics_by_group: dict[int, list[DrawTopicRead]] = {group.id: [] for group in groups}
        for row in rows:
            if row.topic is None:
                continue
            topics_by_group.setdefault(row.group_id, []).append(
                DrawTopicRead(topic_id=row.topic.id, topic_name=row.topic.name)
            )

        return [
            DrawResultRead(group_id=group.id, group_name=group.name, topics=topics_by_group[group.id])
            for group in groups
        ]

    async def _ensure_section_exists(self, section_id: int) -> None:
        if await self.section_repo.get_section_by_id(section_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Секция не найдена")
