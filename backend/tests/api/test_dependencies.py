from unittest.mock import MagicMock

from app.adapters.api import dependencies
from app.repositories.event import EventRepository as SectionEventRepository
from app.repositories.events import EventRepository as EventProgramRepository


def test_section_service_gets_repository_with_exists_by_id():
    service = dependencies.get_section_service(MagicMock())

    assert isinstance(service._event_repository, SectionEventRepository)


def test_event_program_service_gets_program_repository():
    service = dependencies.get_event_program_service(MagicMock())

    assert isinstance(service._event_repo, EventProgramRepository)
