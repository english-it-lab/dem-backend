# app/repositories/__init__.py
from .committee_member import CommitteeMemberRepository
from .events import EventRepository
from .participant import ParticipantRepository
from .poster_content import PosterContentRepository
from .section import SectionRepository
from .technical_requirement import TechnicalRequirementRepository
from .topic import TopicRepository
from .university import UniversityRepository
from .venues import VenueRepository

__all__ = [
    "CommitteeMemberRepository",
    "EventRepository",
    "SectionRepository",
    "ParticipantRepository",
    "PosterContentRepository",
    "TechnicalRequirementRepository",
    "TopicRepository",
    "UniversityRepository",
    "VenueRepository",
]
