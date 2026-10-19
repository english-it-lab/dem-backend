from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal

from annotated_types import MaxLen
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

from app.enums.group import GroupStatus


class ORMModelMixin:
    """Mixin that enables ORM mode for Pydantic models."""

    model_config = ConfigDict(from_attributes=True)


class UniversityBase(BaseModel):
    name: Annotated[str, MaxLen(255)]


class UniversityCreate(UniversityBase):
    pass


class UniversityRead(ORMModelMixin, UniversityBase):
    id: int


class FacultyBase(BaseModel):
    university_id: int | None = None
    name: str


class FacultyCreate(FacultyBase):
    pass


class FacultyRead(ORMModelMixin, FacultyBase):
    id: int


class FacultyUpdate(BaseModel):
    pass


class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(ORMModelMixin, DepartmentBase):
    id: int


class PersonBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    email: str | None = None
    title: str | None = None
    degree: str | None = None
    position: str | None = None
    workplace: str | None = None
    tg_name: str | None = None


class PersonRead(ORMModelMixin, PersonBase):
    id: int


class PersonUpdate(PersonBase):
    id: int


class PersonMyselfUpdate(PersonBase):
    pass


PersonCreate = PersonBase


class JwtFields(StrEnum):
    PERSON_ID = "PERSON_ID"
    EXPIRATION_DATE = "EXPIRATION_DATE"


class AuthPayload(BaseModel):
    PERSON_ID: int
    EXPIRATION_DATE: int

    model_config = {"extra": "forbid"}


class OrganizerBase(BaseModel):
    person_id: int | None = None
    contact_number: str | None = None
    access_key: int | None = None


class OrganizerCreate(OrganizerBase):
    pass


class OrganizerRead(ORMModelMixin, OrganizerBase):
    id: int


class VenueBase(BaseModel):
    city: str | None = None
    street: str | None = None
    building: str | None = None


class VenueCreate(VenueBase):
    pass


class VenueRead(ORMModelMixin, VenueBase):
    id: int


class EventBase(BaseModel):
    venue_id: int | None = None
    organizer_id: int | None = None
    name: str | None = None
    type: str | None = None
    event_date: date | None = None


class EventCreate(EventBase):
    pass


class EventRead(ORMModelMixin, EventBase):
    id: int


class CommitteeMemberBase(BaseModel):
    event_id: int
    person_id: int | None = None
    role: str | None = None
    committee_type: str | None = None
    sort_order: int = Field(default=0)


class CommitteeMemberCreate(CommitteeMemberBase):
    pass


class CommitteeMemberRead(ORMModelMixin, CommitteeMemberBase):
    id: int


class CourseBase(BaseModel):
    year: int | None = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    pass


class CourseRead(ORMModelMixin, CourseBase):
    id: int


class TextbookLevelBase(BaseModel):
    level_abbreviation: str | None = None


class TextbookLevelCreate(TextbookLevelBase):
    pass


class TextbookLevelRead(ORMModelMixin, TextbookLevelBase):
    id: int


class TextbookLevelUpdate(TextbookLevelBase):
    pass


class SectionBase(BaseModel):
    name: str
    lecture_hall: str | None = None
    time: datetime | None = None
    section_type: str | None = None
    time_limit: int | None = None


class SectionCreate(SectionBase):
    event_id: int | None = Field(None)


class SectionUpdate(SectionBase):
    organizer_id: int | None = Field(None)


class SectionRead(ORMModelMixin, SectionBase):
    id: int


class EventSectionBase(BaseModel):
    event_id: int
    section_id: int


class EventSectionCreate(EventSectionBase):
    pass


class EventSectionRead(ORMModelMixin, EventSectionBase):
    id: int


TopicName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)]


class TopicBase(BaseModel):
    section_id: int | None = None
    name: str | None = None


class TopicCreate(BaseModel):
    name: TopicName


class TopicUpdate(BaseModel):
    name: TopicName | None = None
    section_id: int | None = Field(default=None, gt=0)


class TopicRead(ORMModelMixin, TopicBase):
    id: int


class GroupBase(BaseModel):
    section_id: int | None = None
    name: str | None = None
    status: GroupStatus = GroupStatus.FORMING
    member_count: int | None = None
    registration_time: datetime | None = None


class GroupCreate(BaseModel):
    section_id: int
    name: str


class GroupUpdate(BaseModel):
    name: str | None = None


class GroupRead(ORMModelMixin, GroupBase):
    id: int


class GroupFilter(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    section_id: int | None = Field(
        default=None,
        gt=0,
        alias="section-id",
    )
    status: GroupStatus | None = Field(default=None, alias="group-status")


class InviteTokenResponse(BaseModel):
    token: str = Field(description="Токен приглашения")
    expired_at: datetime = Field(description="Время жизни токена")


class GroupTopicBase(BaseModel):
    group_id: int
    topic_id: int | None = None


class GroupTopicCreate(GroupTopicBase):
    pass


class GroupTopicRead(ORMModelMixin, GroupTopicBase):
    id: int


class TeacherBase(BaseModel):
    university_id: int | None = None
    department_id: int | None = None
    person_id: int | None = None


class TeacherCreate(TeacherBase):
    pass


class TeacherRead(ORMModelMixin, TeacherBase):
    id: int


class TeacherUpdate(TeacherBase):
    pass


class ParticipantBase(BaseModel):
    person_id: int | None = None
    faculty_id: int | None = None
    course_id: int | None = None
    teacher_id: int | None = None
    section_id: int | None = None
    is_poster_participant: bool = Field(default=False)
    is_translator_participant: bool = Field(default=False)
    has_translator_education: bool = Field(default=False)
    textbook_level_id: int | None = None
    is_group_leader: bool = Field(default=False)
    presentation_topic: str | None = None
    abstract: str | None = None
    scientific_advisor_id: int | None = None
    presentation_order: int | None = None
    is_notification_allowed: bool = Field(default=True)
    password_hash: str | None = None


class ParticipantCreate(BaseModel):
    person_id: int  # person_id обязателен. Не может быть участника без человека.
    faculty_id: int | None = None
    course_id: int | None = None
    teacher_id: int | None = None
    section_id: int | None = None
    is_poster_participant: bool = Field(default=False)
    is_translator_participant: bool = Field(default=False)
    has_translator_education: bool = Field(default=False)
    textbook_level_id: int | None = None
    is_group_leader: bool = Field(default=False)
    presentation_topic: str | None = None
    is_notification_allowed: bool = Field(default=True)
    password_hash: str | None = None


class ParticipantRead(ORMModelMixin, ParticipantBase):
    id: int


class ParticipantUpdate(BaseModel):
    person_id: int | None = None
    faculty_id: int | None = None
    course_id: int | None = None
    teacher_id: int | None = None
    section_id: int | None = None
    is_poster_participant: bool = Field(default=False)
    is_translator_participant: bool = Field(default=False)
    has_translator_education: bool = Field(default=False)
    textbook_level_id: int | None = None
    is_group_leader: bool = Field(default=False)
    presentation_topic: str | None = None
    is_notification_allowed: bool = Field(default=True)
    password_hash: str | None = None
    abstract: str | None = None
    presentation_order: int | None = None


class GroupParticipantBase(BaseModel):
    group_id: int
    participant_id: int


class GroupParticipantCreate(GroupParticipantBase):
    pass


class GroupParticipantRead(ORMModelMixin, GroupParticipantBase):
    id: int


class JuryBase(BaseModel):
    university_id: int | None = None
    person_id: int | None = None
    is_chairman: bool = Field(default=False)
    access_key: int | None = None


class JuryCreate(JuryBase):
    pass


class JuryRead(ORMModelMixin, JuryBase):
    id: int


class JuryUpdate(BaseModel):
    university_id: int | None = None
    person_id: int | None = None
    is_chairman: bool | None = None
    access_key: int | None = None


class SectionJuryBase(BaseModel):
    section_id: int
    jury_id: int


class SectionJuryCreate(SectionJuryBase):
    pass


class SectionJuryRead(ORMModelMixin, SectionJuryBase):
    id: int


class SectionJuryUpdate(BaseModel):
    section_id: int | None = None
    jury_id: int | None = None


class JuryScoreBase(BaseModel):
    jury_id: int | None = None
    participant_id: int | None = None
    organization_score: float | None = None
    content: float | None = None
    visuals: float | None = None
    mechanics: float | None = None
    delivery: float | None = None
    comment: str | None = None


class JuryScoreCreate(JuryScoreBase):
    @field_validator("organization_score", "content", "visuals", "mechanics", "delivery")
    @classmethod
    def validate_score_range(cls, v: float | None) -> float | None:
        """Validate that scores are between 0.0 and 10.0."""
        if v is not None and (v < 0.0 or v > 10.0):
            raise ValueError("Score must be between 0.0 and 10.0")
        return v


class JuryScoreRead(ORMModelMixin, JuryScoreBase):
    id: int


class JuryScoreUpdate(BaseModel):
    organization_score: float | None = None
    content: float | None = None
    visuals: float | None = None
    mechanics: float | None = None
    delivery: float | None = None
    comment: str | None = None

    @field_validator("organization_score", "content", "visuals", "mechanics", "delivery")
    @classmethod
    def validate_score_range(cls, v: float | None) -> float | None:
        """Validate that scores are between 0.0 and 10.0."""
        if v is not None and (v < 0.0 or v > 10.0):
            raise ValueError("Score must be between 0.0 and 10.0")
        return v


class ParticipantScoreSummary(BaseModel):
    """Summary of all scores for a participant with calculated average."""

    participant_id: int
    scores: list[JuryScoreRead]
    average_score: float | None  # None if no scores exist

    @staticmethod
    def calculate_average(scores: list[JuryScoreRead]) -> float | None:
        """Calculate average of all 5 criteria across all jury scores."""
        if not scores:
            return None

        total_sum = 0.0
        count = 0

        for score in scores:
            for field in ["organization_score", "content", "visuals", "mechanics", "delivery"]:
                value = getattr(score, field)
                if value is not None:
                    total_sum += value
                    count += 1

        return round(total_sum / count, 2) if count > 0 else None


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class ParticipantRankingSortField(StrEnum):
    TOTAL_SCORE = "total_score"
    LAST_NAME = "last_name"
    FIRST_NAME = "first_name"
    RANK = "rank"
    SCORES_COUNT = "scores_count"


class ParticipantRankingRead(BaseModel):
    """Single row from the aggregated leaderboard."""

    participant_id: int
    person_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    section_id: int | None = None
    section_name: str | None = None
    presentation_topic: str | None = None
    total_score: float
    scores_count: int
    rank: int


class ParticipantRankingList(BaseModel):
    """Paginated leaderboard response."""

    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool
    items: list[ParticipantRankingRead]


class JuryScoreChangeBase(BaseModel):
    jury_scores_id: int
    jury_id: int | None = None
    update_time: datetime | None = None


class JuryScoreChangeCreate(JuryScoreChangeBase):
    pass


class JuryScoreChangeRead(ORMModelMixin, JuryScoreChangeBase):
    id: int


class ScoreHistoryBase(BaseModel):
    jury_scores_id: int
    jury_id: int | None = None
    update_time: datetime | None = None


class ScoreHistoryCreate(ScoreHistoryBase):
    pass


class ScoreHistoryRead(ORMModelMixin, ScoreHistoryBase):
    id: int


class ScoreHistoryUpdate(BaseModel):
    jury_scores_id: int | None = None
    jury_id: int | None = None
    update_time: datetime | None = None


class JuryProgressItem(BaseModel):
    participant_id: int
    participant_name: str
    topic: str | None
    is_graded: bool
    current_score: float | None = None  # Average score or amount, if you have already assessed it


class OrganizerSectionChangeBase(BaseModel):
    section_id: int
    organizer_id: int | None = None
    update_time: datetime | None = None


class OrganizerSectionChangeCreate(OrganizerSectionChangeBase):
    pass


class OrganizerSectionChangeRead(ORMModelMixin, OrganizerSectionChangeBase):
    id: int


class OrganizerParticipantChangeBase(BaseModel):
    participant_id: int
    organizer_id: int | None = None
    update_time: datetime | None = None


class OrganizerParticipantChangeCreate(OrganizerParticipantChangeBase):
    pass


class OrganizerParticipantChangeRead(ORMModelMixin, OrganizerParticipantChangeBase):
    id: int


class TechnicalRequirementBase(BaseModel):
    topic_id: int | None = None
    format: Literal["PDF", "PNG", "JPG", "JPEG"] | None = None
    sizes: Literal["A4", "A3", "A2", "A1"] | None = None

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.upper()
        return v


class TechnicalRequirementCreate(TechnicalRequirementBase):
    pass


class TechnicalRequirementRead(ORMModelMixin, TechnicalRequirementBase):
    id: int


class TechnicalRequirementUpdate(BaseModel):
    topic_id: int | None = None
    format: Literal["PDF", "PNG", "JPG", "JPEG"] | None = None
    sizes: Literal["A4", "A3", "A2", "A1"] | None = None

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.upper()
        return v


class TechnicalRequirementReadWithContent(ORMModelMixin, TechnicalRequirementBase):
    id: int
    posters_content: list[PosterContentRead] = []


class PosterContentBase(BaseModel):
    technical_requirements_id: int | None = None
    words_amount: int | None = None
    images_amount: int | None = None


class PosterContentCreate(PosterContentBase):
    pass


class PosterContentRead(ORMModelMixin, PosterContentBase):
    id: int


class PosterContentUpdate(BaseModel):
    technical_requirements_id: int | None = None
    words_amount: int | None = None
    images_amount: int | None = None


class EmailCodeRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    code: str


class LoginResponse(ORMModelMixin, BaseModel):
    access_token: str
    token_type: str = "bearer"


__all__ = [
    "ORMModelMixin",
    "UniversityBase",
    "UniversityCreate",
    "UniversityRead",
    "FacultyBase",
    "FacultyCreate",
    "FacultyRead",
    "FacultyUpdate",
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentRead",
    "PersonBase",
    "PersonCreate",
    "PersonRead",
    "OrganizerBase",
    "OrganizerCreate",
    "OrganizerRead",
    "VenueBase",
    "VenueCreate",
    "VenueRead",
    "EventBase",
    "EventCreate",
    "EventRead",
    "CommitteeMemberBase",
    "CommitteeMemberCreate",
    "CommitteeMemberRead",
    "CourseBase",
    "CourseCreate",
    "CourseRead",
    "CourseUpdate",
    "TextbookLevelBase",
    "TextbookLevelCreate",
    "TextbookLevelRead",
    "SectionBase",
    "SectionCreate",
    "SectionUpdate",
    "SectionRead",
    "EventSectionBase",
    "EventSectionCreate",
    "EventSectionRead",
    "TopicBase",
    "TopicCreate",
    "TopicUpdate",
    "TopicRead",
    "GroupBase",
    "GroupCreate",
    "GroupUpdate",
    "GroupRead",
    "GroupFilter",
    "GroupTopicBase",
    "GroupTopicCreate",
    "GroupTopicRead",
    "InviteTokenResponse",
    "TeacherBase",
    "TeacherCreate",
    "TeacherRead",
    "ParticipantBase",
    "ParticipantCreate",
    "ParticipantRead",
    "ParticipantUpdate",
    "GroupParticipantBase",
    "GroupParticipantCreate",
    "GroupParticipantRead",
    "JuryBase",
    "JuryCreate",
    "JuryRead",
    "SectionJuryBase",
    "SectionJuryCreate",
    "SectionJuryRead",
    "JuryScoreBase",
    "JuryScoreCreate",
    "JuryScoreRead",
    "JuryScoreUpdate",
    "ParticipantScoreSummary",
    "SortOrder",
    "ParticipantRankingSortField",
    "ParticipantRankingRead",
    "ParticipantRankingList",
    "JuryScoreChangeBase",
    "JuryScoreChangeCreate",
    "JuryScoreChangeRead",
    "OrganizerSectionChangeBase",
    "OrganizerSectionChangeCreate",
    "OrganizerSectionChangeRead",
    "OrganizerParticipantChangeBase",
    "OrganizerParticipantChangeCreate",
    "OrganizerParticipantChangeRead",
    "TechnicalRequirementBase",
    "TechnicalRequirementCreate",
    "TechnicalRequirementRead",
    "TechnicalRequirementUpdate",
    "TechnicalRequirementReadWithContent",
    "PosterContentBase",
    "PosterContentCreate",
    "PosterContentRead",
    "PosterContentUpdate",
    "JuryProgressItem",
    "EmailCodeRequest",
    "LoginRequest",
    "LoginResponse",
    "TextbookLevelUpdate",
    "TeacherUpdate",
]
