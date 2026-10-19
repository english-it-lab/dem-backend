from unittest.mock import MagicMock

from app.adapters.api import dependencies
from app.repositories.event import EventRepository


def test_section_service_gets_event_repository():
    service = dependencies.get_section_service(MagicMock())

    assert isinstance(service._event_repository, EventRepository)


def test_event_program_service_gets_event_repository():
    service = dependencies.get_event_program_service(MagicMock())

    assert isinstance(service._event_repo, EventRepository)
