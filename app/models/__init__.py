from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.enums.group import GroupStatus


class Base(DeclarativeBase):
    pass


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    faculties: Mapped[list[Faculty]] = relationship(back_populates="university")
    teachers: Mapped[list[Teacher]] = relationship(back_populates="university")
    juries: Mapped[list[Jury]] = relationship(back_populates="university")


class Faculty(Base):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int | None] = mapped_column(ForeignKey("universities.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    university: Mapped[University | None] = relationship(back_populates="faculties")
    participants: Mapped[list[Participant]] = relationship(back_populates="faculty")


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    teachers: Mapped[list[Teacher]] = relationship(back_populates="department")


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    middle_name: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(20))
    degree: Mapped[str | None] = mapped_column(String(20))
    position: Mapped[str | None] = mapped_column(String(50))
    workplace: Mapped[str | None] = mapped_column(String(50))
    tg_name: Mapped[str | None] = mapped_column(String(32))

    organizers: Mapped[list[Organizer]] = relationship(back_populates="person")
    teachers: Mapped[list[Teacher]] = relationship(back_populates="person")
    participants: Mapped[list[Participant]] = relationship(
        back_populates="person", foreign_keys="Participant.person_id"
    )
    juries: Mapped[list[Jury]] = relationship(back_populates="person")
    committee_members: Mapped[list[CommitteeMember]] = relationship(back_populates="person")
    scientific_advisees: Mapped[list[Participant]] = relationship(
        back_populates="scientific_advisor", foreign_keys="Participant.scientific_advisor_id"
    )

    @property
    def is_profile_complete(self) -> bool:
        required_fields = [
            self.first_name,
            self.last_name,
            self.middle_name,
            self.title,
            self.degree,
            self.position,
            self.workplace,
            self.tg_name,
        ]

        return all(field is not None for field in required_fields)


class Organizer(Base):
    __tablename__ = "organizers"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id", ondelete="SET NULL"))
    contact_number: Mapped[str | None] = mapped_column(String(15))
    access_key: Mapped[int | None] = mapped_column(BigInteger)

    person: Mapped[Person | None] = relationship(back_populates="organizers")
    events: Mapped[list[Event]] = relationship(back_populates="organizer")
    section_changes: Mapped[list[OrganizerSectionChange]] = relationship(back_populates="organizer")
    participant_changes: Mapped[list[OrganizerParticipantChange]] = relationship(back_populates="organizer")


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str | None] = mapped_column(String(100))
    street: Mapped[str | None] = mapped_column(String(100))
    building: Mapped[str | None] = mapped_column(String(10))

    events: Mapped[list[Event]] = relationship(back_populates="venue")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id", ondelete="SET NULL"))
    organizer_id: Mapped[int | None] = mapped_column(ForeignKey("organizers.id", ondelete="SET NULL"))
    name: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str | None] = mapped_column(String(100))
    event_date: Mapped[Date | None] = mapped_column(Date)

    venue: Mapped[Venue | None] = relationship(back_populates="events")
    organizer: Mapped[Organizer | None] = relationship(back_populates="events")
    event_sections: Mapped[list[EventSection]] = relationship(back_populates="event")
    committee_members: Mapped[list[CommitteeMember]] = relationship(back_populates="event")


class CommitteeMember(Base):
    __tablename__ = "committee_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id", ondelete="SET NULL"))
    role: Mapped[str | None] = mapped_column(String(100))
    committee_type: Mapped[str | None] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    event: Mapped[Event] = relationship(back_populates="committee_members")
    person: Mapped[Person | None] = relationship(back_populates="committee_members")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int | None] = mapped_column(Integer)

    participants: Mapped[list[Participant]] = relationship(back_populates="course")


class TextbookLevel(Base):
    __tablename__ = "textbook_levels"

    id: Mapped[int] = mapped_column(primary_key=True)
    level_abbreviation: Mapped[str | None] = mapped_column(String(3))

    participants: Mapped[list[Participant]] = relationship(back_populates="textbook_level")


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    lecture_hall: Mapped[str | None] = mapped_column(String(7))
    time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    section_type: Mapped[str | None] = mapped_column(String(50))
    time_limit: Mapped[int | None] = mapped_column(Integer)

    topics: Mapped[list[Topic]] = relationship(back_populates="section")
    groups: Mapped[list[Group]] = relationship(back_populates="section")
    participants: Mapped[list[Participant]] = relationship(back_populates="section")
    section_juries: Mapped[list[SectionJury]] = relationship(back_populates="section")
    organizer_changes: Mapped[list[OrganizerSectionChange]] = relationship(back_populates="section")
    event_links: Mapped[list[EventSection]] = relationship(back_populates="section")


class EventSection(Base):
    __tablename__ = "event_sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"))

    event: Mapped[Event] = relationship(back_populates="event_sections")
    section: Mapped[Section] = relationship(back_populates="event_links")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int | None] = mapped_column(ForeignKey("sections.id", ondelete="SET NULL"))
    name: Mapped[str | None] = mapped_column(String(50))

    section: Mapped[Section | None] = relationship(back_populates="topics")
    technical_requirements: Mapped[list[TechnicalRequirement]] = relationship(back_populates="topic")
    group_topics: Mapped[list[GroupTopic]] = relationship(back_populates="topic")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int | None] = mapped_column(ForeignKey("sections.id", ondelete="SET NULL"))
    name: Mapped[str | None] = mapped_column(String(100))

    status: Mapped[GroupStatus] = mapped_column(
        SQLEnum(GroupStatus),
        default=GroupStatus.FORMING,
        nullable=False,
    )

    member_count: Mapped[int | None] = mapped_column(Integer)
    registration_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    section: Mapped[Section | None] = relationship(back_populates="groups")
    group_topics: Mapped[list[GroupTopic]] = relationship(back_populates="group")
    group_participants: Mapped[list[GroupParticipant]] = relationship(back_populates="group")


class GroupTopic(Base):
    __tablename__ = "group_topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"))

    group: Mapped[Group] = relationship(back_populates="group_topics")
    topic: Mapped[Topic | None] = relationship(back_populates="group_topics")


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int | None] = mapped_column(ForeignKey("universities.id", ondelete="SET NULL"))
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id", ondelete="SET NULL"))

    university: Mapped[University | None] = relationship(back_populates="teachers")
    department: Mapped[Department | None] = relationship(back_populates="teachers")
    person: Mapped[Person | None] = relationship(back_populates="teachers")
    participants: Mapped[list[Participant]] = relationship(back_populates="teacher")


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id", ondelete="SET NULL"))
    faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculties.id", ondelete="SET NULL"))
    course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"))
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("teachers.id", ondelete="SET NULL"))
    section_id: Mapped[int | None] = mapped_column(ForeignKey("sections.id", ondelete="SET NULL"))
    is_poster_participant: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_translator_participant: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    has_translator_education: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    textbook_level_id: Mapped[int | None] = mapped_column(ForeignKey("textbook_levels.id", ondelete="SET NULL"))
    is_group_leader: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    presentation_topic: Mapped[str | None] = mapped_column(String(255))
    abstract: Mapped[str | None] = mapped_column(Text)
    scientific_advisor_id: Mapped[int | None] = mapped_column(ForeignKey("people.id", ondelete="SET NULL"))
    presentation_order: Mapped[int | None] = mapped_column(Integer)
    is_notification_allowed: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    password_hash: Mapped[str | None] = mapped_column(String(255))

    person: Mapped[Person | None] = relationship(back_populates="participants", foreign_keys=[person_id])
    faculty: Mapped[Faculty | None] = relationship(back_populates="participants")
    course: Mapped[Course | None] = relationship(back_populates="participants")
    teacher: Mapped[Teacher | None] = relationship(back_populates="participants")
    section: Mapped[Section | None] = relationship(back_populates="participants")
    textbook_level: Mapped[TextbookLevel | None] = relationship(back_populates="participants")
    scientific_advisor: Mapped[Person | None] = relationship(
        back_populates="scientific_advisees", foreign_keys=[scientific_advisor_id]
    )
    group_participants: Mapped[list[GroupParticipant]] = relationship(back_populates="participant")
    jury_scores: Mapped[list[JuryScore]] = relationship(back_populates="participant")
    organizer_changes: Mapped[list[OrganizerParticipantChange]] = relationship(back_populates="participant")

    @property
    def is_profile_complete(self) -> bool:
        required_fields = [
            # self.faculty_id,
            # self.course_id,
            # self.teacher_id,
            # self.textbook_level_id,
            self.presentation_topic,
            self.abstract,
            # self.scientific_advisor,
            self.presentation_order,
        ]

        return all(field is not None for field in required_fields)


class GroupParticipant(Base):
    __tablename__ = "group_participants"
    __table_args__ = (UniqueConstraint("group_id", "participant_id", name="uq_group_participant"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id", ondelete="CASCADE"))

    group: Mapped[Group] = relationship(back_populates="group_participants")
    participant: Mapped[Participant] = relationship(back_populates="group_participants")


class Jury(Base):
    __tablename__ = "juries"

    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int | None] = mapped_column(ForeignKey("universities.id", ondelete="SET NULL"))
    person_id: Mapped[int | None] = mapped_column(ForeignKey("people.id", ondelete="SET NULL"))
    is_chairman: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    access_key: Mapped[int | None] = mapped_column(BigInteger)

    university: Mapped[University | None] = relationship(back_populates="juries")
    person: Mapped[Person | None] = relationship(back_populates="juries")
    section_juries: Mapped[list[SectionJury]] = relationship(back_populates="jury")
    jury_scores: Mapped[list[JuryScore]] = relationship(back_populates="jury")
    jury_score_changes: Mapped[list[JuryScoreChange]] = relationship(back_populates="jury")


class SectionJury(Base):
    __tablename__ = "section_juries"
    __table_args__ = (UniqueConstraint("section_id", "jury_id", name="uq_section_jury"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"))
    jury_id: Mapped[int] = mapped_column(ForeignKey("juries.id", ondelete="CASCADE"))

    section: Mapped[Section] = relationship(back_populates="section_juries")
    jury: Mapped[Jury] = relationship(back_populates="section_juries")


class JuryScore(Base):
    __tablename__ = "jury_scores"
    __table_args__ = (UniqueConstraint("jury_id", "participant_id", name="uq_jury_participant_score"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    jury_id: Mapped[int | None] = mapped_column(ForeignKey("juries.id", ondelete="SET NULL"))
    participant_id: Mapped[int | None] = mapped_column(ForeignKey("participants.id", ondelete="SET NULL"))
    organization_score: Mapped[float | None] = mapped_column(Float)
    content: Mapped[float | None] = mapped_column(Float)
    visuals: Mapped[float | None] = mapped_column(Float)
    mechanics: Mapped[float | None] = mapped_column(Float)
    delivery: Mapped[float | None] = mapped_column(Float)
    comment: Mapped[str | None] = mapped_column(String(100))

    jury: Mapped[Jury | None] = relationship(back_populates="jury_scores")
    participant: Mapped[Participant | None] = relationship(back_populates="jury_scores")
    changes: Mapped[list[JuryScoreChange]] = relationship(back_populates="jury_score")


class JuryScoreChange(Base):
    __tablename__ = "jury_scores_changes"

    id: Mapped[int] = mapped_column(primary_key=True)
    jury_scores_id: Mapped[int] = mapped_column(ForeignKey("jury_scores.id", ondelete="CASCADE"))
    jury_id: Mapped[int | None] = mapped_column(ForeignKey("juries.id", ondelete="SET NULL"))
    update_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    jury_score: Mapped[JuryScore] = relationship(back_populates="changes")
    jury: Mapped[Jury | None] = relationship(back_populates="jury_score_changes")


class OrganizerSectionChange(Base):
    __tablename__ = "organizer_section_changes"

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"))
    organizer_id: Mapped[int | None] = mapped_column(ForeignKey("organizers.id", ondelete="SET NULL"))
    update_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    section: Mapped[Section] = relationship(back_populates="organizer_changes")
    organizer: Mapped[Organizer | None] = relationship(back_populates="section_changes")


class OrganizerParticipantChange(Base):
    __tablename__ = "organizer_participant_changes"

    id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id", ondelete="CASCADE"))
    organizer_id: Mapped[int | None] = mapped_column(ForeignKey("organizers.id", ondelete="SET NULL"))
    update_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    participant: Mapped[Participant] = relationship(back_populates="organizer_changes")
    organizer: Mapped[Organizer | None] = relationship(back_populates="participant_changes")


class TechnicalRequirement(Base):
    __tablename__ = "technical_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"))
    format: Mapped[str | None] = mapped_column(String(10))
    sizes: Mapped[str | None] = mapped_column(String(2))

    topic: Mapped[Topic | None] = relationship(back_populates="technical_requirements")
    posters_content: Mapped[list[PosterContent]] = relationship(back_populates="technical_requirement")


class PosterContent(Base):
    __tablename__ = "posters_content"

    id: Mapped[int] = mapped_column(primary_key=True)
    technical_requirements_id: Mapped[int | None] = mapped_column(
        ForeignKey("technical_requirements.id", ondelete="SET NULL")
    )
    words_amount: Mapped[int | None] = mapped_column(Integer)
    images_amount: Mapped[int | None] = mapped_column(Integer)

    technical_requirement: Mapped[TechnicalRequirement | None] = relationship(back_populates="posters_content")


__all__ = [
    "Base",
    "University",
    "Faculty",
    "Department",
    "Person",
    "Organizer",
    "Venue",
    "Event",
    "CommitteeMember",
    "Course",
    "TextbookLevel",
    "Section",
    "EventSection",
    "Topic",
    "Group",
    "GroupTopic",
    "Teacher",
    "Participant",
    "GroupParticipant",
    "Jury",
    "SectionJury",
    "JuryScore",
    "JuryScoreChange",
    "OrganizerSectionChange",
    "OrganizerParticipantChange",
    "TechnicalRequirement",
    "PosterContent",
]
