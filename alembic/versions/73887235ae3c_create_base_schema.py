"""create base schema

Revision ID: 73887235ae3c
Revises: 
Create Date: 2025-12-07 16:53:09.797104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "73887235ae3c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "universities",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
    )

    op.create_table(
        "faculties",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("university_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
    )

    op.create_table(
        "people",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("middle_name", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=20), nullable=True),
        sa.Column("degree", sa.String(length=20), nullable=True),
        sa.Column("position", sa.String(length=50), nullable=True),
        sa.Column("workplace", sa.String(length=50), nullable=True),
        sa.Column("tg_name", sa.String(length=32), nullable=True),
    )

    op.create_table(
        "organizers",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("person_id", sa.Integer(), nullable=True),
        sa.Column("contact_number", sa.String(length=15), nullable=True),
        sa.Column("access_key", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["person_id"], ["people.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "venues",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("street", sa.String(length=100), nullable=True),
        sa.Column("building", sa.String(length=10), nullable=True),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("venue_id", sa.Integer(), nullable=True),
        sa.Column("organizer_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=100), nullable=True),
        sa.Column("event_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["organizer_id"], ["organizers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["venue_id"], ["venues.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=True),
    )

    op.create_table(
        "textbook_levels",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("level_abbreviation", sa.String(length=3), nullable=True),
    )

    op.create_table(
        "sections",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("lecture_hall", sa.String(length=7), nullable=True),
        sa.Column("time", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "event_sections",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("section_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("section_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("section_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("member_count", sa.Integer(), nullable=True),
        sa.Column("registration_time", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "group_topics",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("university_id", sa.Integer(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("person_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["person_id"], ["people.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "participants",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("person_id", sa.Integer(), nullable=True),
        sa.Column("faculty_id", sa.Integer(), nullable=True),
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("teacher_id", sa.Integer(), nullable=True),
        sa.Column("section_id", sa.Integer(), nullable=True),
        sa.Column("is_poster_participant", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_translator_participant", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("has_translator_education", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("textbook_level_id", sa.Integer(), nullable=True),
        sa.Column("is_group_leader", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("presentation_topic", sa.String(length=255), nullable=True),
        sa.Column("is_notification_allowed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["person_id"], ["people.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["textbook_level_id"], ["textbook_levels.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "group_participants",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["participant_id"], ["participants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("group_id", "participant_id", name="uq_group_participant"),
    )

    op.create_table(
        "juries",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("university_id", sa.Integer(), nullable=True),
        sa.Column("person_id", sa.Integer(), nullable=True),
        sa.Column("is_chairman", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("access_key", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["person_id"], ["people.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "section_juries",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("section_id", sa.Integer(), nullable=False),
        sa.Column("jury_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["jury_id"], ["juries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("section_id", "jury_id", name="uq_section_jury"),
    )

    op.create_table(
        "jury_scores",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("jury_id", sa.Integer(), nullable=True),
        sa.Column("participant_id", sa.Integer(), nullable=True),
        sa.Column("organization_score", sa.Float(), nullable=True),
        sa.Column("content", sa.Float(), nullable=True),
        sa.Column("visuals", sa.Float(), nullable=True),
        sa.Column("mechanics", sa.Float(), nullable=True),
        sa.Column("delivery", sa.Float(), nullable=True),
        sa.Column("comment", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["jury_id"], ["juries.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["participant_id"], ["participants.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "jury_scores_changes",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("jury_scores_id", sa.Integer(), nullable=False),
        sa.Column("jury_id", sa.Integer(), nullable=True),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["jury_id"], ["juries.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["jury_scores_id"], ["jury_scores.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "organizer_section_changes",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("section_id", sa.Integer(), nullable=False),
        sa.Column("organizer_id", sa.Integer(), nullable=True),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["organizer_id"], ["organizers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "organizer_participant_changes",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("organizer_id", sa.Integer(), nullable=True),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["organizer_id"], ["organizers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["participant_id"], ["participants.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "technical_requirements",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("topic_id", sa.Integer(), nullable=True),
        sa.Column("format", sa.String(length=10), nullable=True),
        sa.Column("sizes", sa.String(length=2), nullable=True),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "posters_content",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("technical_requirements_id", sa.Integer(), nullable=True),
        sa.Column("words_amount", sa.Integer(), nullable=True),
        sa.Column("images_amount", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["technical_requirements_id"], ["technical_requirements.id"], ondelete="SET NULL"),
    )


def downgrade() -> None:
    op.drop_table("posters_content")
    op.drop_table("technical_requirements")
    op.drop_table("organizer_participant_changes")
    op.drop_table("organizer_section_changes")
    op.drop_table("jury_scores_changes")
    op.drop_table("jury_scores")
    op.drop_table("section_juries")
    op.drop_table("juries")
    op.drop_table("group_participants")
    op.drop_table("participants")
    op.drop_table("teachers")
    op.drop_table("group_topics")
    op.drop_table("groups")
    op.drop_table("topics")
    op.drop_table("event_sections")
    op.drop_table("sections")
    op.drop_table("textbook_levels")
    op.drop_table("courses")
    op.drop_table("events")
    op.drop_table("venues")
    op.drop_table("organizers")
    op.drop_table("people")
    op.drop_table("departments")
    op.drop_table("faculties")
    op.drop_table("universities")
