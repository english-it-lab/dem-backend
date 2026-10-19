import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from app.schemas import GroupFilter
from app.services.draw import DrawService


def make_service(groups, rows, topics=()):
    topic_repo = MagicMock()
    topic_repo.list_topics = AsyncMock(return_value=list(topics))
    group_repo = MagicMock()
    group_repo.list_groups = AsyncMock(return_value=groups)
    group_topic_repo = MagicMock()
    group_topic_repo.get_by_section = AsyncMock(return_value=rows)
    group_topic_repo.clear_section = AsyncMock()
    group_topic_repo.create = AsyncMock()
    return DrawService(topic_repo, group_repo, group_topic_repo), topic_repo, group_repo, group_topic_repo


def test_get_results_groups_rows_by_group_and_keeps_empty_groups():
    alpha = SimpleNamespace(id=1, name="Alpha")
    beta = SimpleNamespace(id=2, name="Beta")
    rows = [
        SimpleNamespace(group_id=1, group=alpha, topic=SimpleNamespace(id=10, name="Machine learning")),
        SimpleNamespace(group_id=1, group=alpha, topic=SimpleNamespace(id=11, name="Databases")),
        SimpleNamespace(group_id=1, group=alpha, topic=None),  # topic deleted after the draw
    ]
    service, _, group_repo, _ = make_service([alpha, beta], rows)

    results = asyncio.run(service.get_results(3))

    group_repo.list_groups.assert_called_once_with(GroupFilter(section_id=3))
    assert [r.model_dump() for r in results] == [
        {
            "group_id": 1,
            "group_name": "Alpha",
            "topics": [
                {"topic_id": 10, "topic_name": "Machine learning"},
                {"topic_id": 11, "topic_name": "Databases"},
            ],
        },
        {"group_id": 2, "group_name": "Beta", "topics": []},
    ]


def test_run_draw_assigns_every_topic_and_persists_assignments():
    groups = [SimpleNamespace(id=1, name="Alpha"), SimpleNamespace(id=2, name="Beta")]
    topics = [
        SimpleNamespace(id=10, name="T10"),
        SimpleNamespace(id=11, name="T11"),
        SimpleNamespace(id=12, name="T12"),
    ]
    service, _, _, group_topic_repo = make_service(groups, [], topics)

    result = asyncio.run(service.run_draw(3))

    assert result.section_id == 3
    assert result.total_topics == 3
    assert result.total_groups == 2
    assert result.empty_groups == []
    assert sorted(len(r.topics) for r in result.results) == [1, 2]
    assigned = sorted(t.topic_id for r in result.results for t in r.topics)
    assert assigned == [10, 11, 12]
    group_topic_repo.clear_section.assert_awaited_once_with(3)
    assert group_topic_repo.create.await_count == 3


def test_run_draw_reports_groups_left_without_topics():
    groups = [SimpleNamespace(id=1, name="Alpha"), SimpleNamespace(id=2, name="Beta")]
    topics = [SimpleNamespace(id=10, name="T10")]
    service, *_ = make_service(groups, [], topics)

    result = asyncio.run(service.run_draw(3))

    assert len(result.empty_groups) == 1
    assert sum(len(r.topics) for r in result.results) == 1
