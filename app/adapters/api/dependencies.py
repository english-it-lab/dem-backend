from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.committee_member import CommitteeMemberRepository
from app.repositories.course import CourseRepository
from app.repositories.event import EventRepository
from app.repositories.faculty import FacultyRepository
from app.repositories.group import GroupRepository
from app.repositories.group_participant import GroupParticipantRepository
from app.repositories.group_topic import GroupTopicRepository
from app.repositories.jury import JuryRepository
from app.repositories.jury_score import JuryScoreRepository
from app.repositories.organizer import OrganizerRepository
from app.repositories.participant import ParticipantRepository
from app.repositories.participant_ranking import ParticipantRankingRepository
from app.repositories.person import PersonRepository
from app.repositories.poster_content import PosterContentRepository
from app.repositories.score_history import ScoreHistoryRepository
from app.repositories.section import SectionRepository
from app.repositories.section_jury import SectionJuryRepository
from app.repositories.teacher import TeacherRepository
from app.repositories.technical_requirement import (
    TechnicalRequirementRepository,
)
from app.repositories.textbook_level import TextbookLevelRepository
from app.repositories.topic import TopicRepository
from app.repositories.university import UniversityRepository
from app.repositories.venue import VenueRepository
from app.schemas import AuthPayload
from app.services.auth import AuthService
from app.services.committee import CommitteeService
from app.services.doc_generator import DocGeneratorService
from app.services.draw import DrawService
from app.services.email_confirmation import EmailConfirmationService
from app.services.event import EventProgramService
from app.services.group import GroupService
from app.services.group_invites import GroupInviteService
from app.services.jury import JuryService
from app.services.jury_score import JuryScoreService
from app.services.jwt import JwtService
from app.services.organizer import OrganizerService
from app.services.participant import ParticipantService
from app.services.participant_ranking import ParticipantRankingService
from app.services.pdf_generator import PDFGeneratorService
from app.services.person import PersonService
from app.services.poster_content import PosterContentService
from app.services.score_history import ScoreHistoryService
from app.services.section import SectionService
from app.services.section_jury import SectionJuryService
from app.services.technical_requirement import TechnicalRequirementService
from app.services.topic import TopicService
from app.services.university import UniversityService
from app.services.venue import VenueService


async def get_session() -> AsyncIterator[AsyncSession]:
    async for session in get_db_session():
        yield session


def get_university_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UniversityService:
    repository = UniversityRepository(session)
    return UniversityService(repository)


def get_technical_requirement_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TechnicalRequirementService:
    repository = TechnicalRequirementRepository(session)
    topic_repository = TopicRepository(session)
    return TechnicalRequirementService(repository, topic_repository)


def get_poster_content_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PosterContentService:
    repository = PosterContentRepository(session)
    tech_req_repository = TechnicalRequirementRepository(session)
    return PosterContentService(repository, tech_req_repository)


def get_jury_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JuryService:
    jury_repository = JuryRepository(session)
    university_repository = UniversityRepository(session)
    person_repository = PersonRepository(session)
    return JuryService(
        jury_repository=jury_repository,
        university_repository=university_repository,
        person_repository=person_repository,
    )


def get_jury_score_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JuryScoreService:
    """Dependency injection for JuryScoreService."""
    jury_score_repo = JuryScoreRepository(session)
    participant_repo = ParticipantRepository(session)
    jury_repo = JuryRepository(session)
    section_jury_repo = SectionJuryRepository(session)

    return JuryScoreService(
        jury_score_repository=jury_score_repo,
        participant_repository=participant_repo,
        jury_repository=jury_repo,
        section_jury_repository=section_jury_repo,
    )


def get_score_history_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ScoreHistoryService:
    score_history_repo = ScoreHistoryRepository(session)
    jury_score_repo = JuryScoreRepository(session)
    jury_repo = JuryRepository(session)
    return ScoreHistoryService(
        score_history_repository=score_history_repo,
        jury_score_repository=jury_score_repo,
        jury_repository=jury_repo,
    )


def get_section_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SectionService:
    repository = SectionRepository(session)
    organizer_repository = OrganizerRepository(session)
    event_repository = EventRepository(session)
    return SectionService(repository, organizer_repository, event_repository)


def get_participant_ranking_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ParticipantRankingService:
    repository = ParticipantRankingRepository(session)
    return ParticipantRankingService(repository)


def get_topic_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TopicService:
    topic_repository = TopicRepository(session)
    section_repository = SectionRepository(session)
    return TopicService(topic_repository, section_repository)


def get_draw_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DrawService:
    return DrawService(
        topic_repo=TopicRepository(session),
        group_repo=GroupRepository(session),
        group_topic_repo=GroupTopicRepository(session),
        section_repo=SectionRepository(session),
    )


def get_section_jury_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SectionJuryService:
    repository = SectionJuryRepository(session)
    section_repository = SectionRepository(session)
    jury_repository = JuryRepository(session)
    return SectionJuryService(
        section_jury_repository=repository,
        section_repository=section_repository,
        jury_repository=jury_repository,
    )


def get_person_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SectionRepository:
    return PersonRepository(session)


def get_event_program_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EventProgramService:
    """Dependency for event program service."""
    event_repo = EventRepository(session)
    section_repo = SectionRepository(session)
    participant_repo = ParticipantRepository(session)
    committee_repo = CommitteeMemberRepository(session)
    section_jury_repo = SectionJuryRepository(session)
    return EventProgramService(event_repo, section_repo, participant_repo, committee_repo, section_jury_repo)


def get_committee_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CommitteeService:
    repository = CommitteeMemberRepository(session)
    return CommitteeService(repository)


def get_pdf_generator_service() -> PDFGeneratorService:
    """Dependency for PDF generator service."""
    return PDFGeneratorService()


def get_doc_generator_service() -> DocGeneratorService:
    """Dependency for DOC generator service."""
    return DocGeneratorService()


def get_venue_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VenueService:
    repository = VenueRepository(session)
    return VenueService(repository)


def get_organizer_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizerRepository:
    return OrganizerRepository(session)


def get_organizer_service(
    repository: Annotated[OrganizerRepository, Depends(get_organizer_repository)],
) -> OrganizerService:
    return OrganizerService(repository)


def get_person_service(
    person_repository: Annotated[PersonRepository, Depends(get_person_repository)],
) -> PersonService:
    return PersonService(person_repository=person_repository)


def get_jwt_service() -> JwtService:
    return JwtService()


def get_email_confirmation_service() -> EmailConfirmationService:
    return EmailConfirmationService()


def get_section_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SectionRepository:
    return SectionRepository(session)


def get_group_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GroupRepository:
    return GroupRepository(session)


def get_group_participant_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GroupParticipantRepository:
    return GroupParticipantRepository(session=session)


def get_participant_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> ParticipantRepository:
    return ParticipantRepository(session=session)


def get_group_service(
    group_repository: Annotated[GroupRepository, Depends(get_group_repository)],
    organizer_repository: Annotated[OrganizerRepository, Depends(get_organizer_repository)],
    section_repository: Annotated[SectionRepository, Depends(get_section_repository)],
    group_participant_repository: Annotated[GroupParticipantRepository, Depends(get_group_participant_repository)],
    participant_repository: Annotated[ParticipantRepository, Depends(get_participant_repository)],
    person_repository: Annotated[PersonRepository, Depends(get_person_repository)],
) -> GroupService:
    return GroupService(
        repository=group_repository,
        organizer_repository=organizer_repository,
        section_repository=section_repository,
        group_participant_repository=group_participant_repository,
        participant_repository=participant_repository,
        person_repository=person_repository,
    )


def get_group_invite_service(
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
    group_repository: Annotated[GroupRepository, Depends(get_group_repository)],
    group_participant_repository: Annotated[GroupParticipantRepository, Depends(get_group_participant_repository)],
    participant_repository: Annotated[ParticipantRepository, Depends(get_participant_repository)],
    person_repository: Annotated[PersonRepository, Depends(get_person_repository)],
) -> GroupInviteService:
    return GroupInviteService(
        jwt_service=jwt_service,
        group_repository=group_repository,
        group_participant_repository=group_participant_repository,
        participant_repository=participant_repository,
        person_repository=person_repository,
    )


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthService:
    email_service = get_email_confirmation_service()
    jwt_service = get_jwt_service()
    person_repository = PersonRepository(session)
    return AuthService(email_service, jwt_service, person_repository)


security = HTTPBearer()


async def get_jwt_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
) -> AuthPayload:
    no_bearer_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    invalid_jwt_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials or credentials.scheme.lower() != "bearer":
        raise no_bearer_token_exception

    jwt_token = credentials.credentials

    try:
        payload = await jwt_service.decode_auth_jwt(jwt_token)
    except Exception as exc:
        raise invalid_jwt_exception from exc

    return payload


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
) -> int:
    return (await get_jwt_payload(credentials, jwt_service)).PERSON_ID


def get_participant_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ParticipantService:
    repository = ParticipantRepository(session)
    faculty_repository = FacultyRepository(session)
    course_repository = CourseRepository(session)
    teacher_repository = TeacherRepository(session)
    section_repository = SectionRepository(session)
    person_repository = PersonRepository(session)
    textbook_level_repository = TextbookLevelRepository(session)
    return ParticipantService(
        repository=repository,
        faculty_repository=faculty_repository,
        course_repository=course_repository,
        teacher_repository=teacher_repository,
        section_repository=section_repository,
        person_repository=person_repository,
        textbook_level_repository=textbook_level_repository,
    )
