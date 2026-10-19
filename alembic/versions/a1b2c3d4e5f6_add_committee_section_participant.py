"""add committee, section type, participant fields

Revision ID: a1b2c3d4e5f6
Revises: f9d10ab9bc1c
Create Date: 2026-05-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "1bc6b59ad6ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sections", sa.Column("section_type", sa.String(50), nullable=True))
    op.add_column("sections", sa.Column("time_limit", sa.Integer(), nullable=True))

    op.add_column("participants", sa.Column("abstract", sa.Text(), nullable=True))
    op.add_column("participants", sa.Column("scientific_advisor_id", sa.Integer(), nullable=True))
    op.add_column("participants", sa.Column("presentation_order", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_participants_scientific_advisor_id",
        "participants",
        "people",
        ["scientific_advisor_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "committee_members",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("person_id", sa.Integer(), sa.ForeignKey("people.id", ondelete="SET NULL"), nullable=True),
        sa.Column("role", sa.String(100), nullable=True),
        sa.Column("committee_type", sa.String(50), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_table("committee_members")

    op.drop_constraint("fk_participants_scientific_advisor_id", "participants", type_="foreignkey")
    op.drop_column("participants", "presentation_order")
    op.drop_column("participants", "scientific_advisor_id")
    op.drop_column("participants", "abstract")

    op.drop_column("sections", "time_limit")
    op.drop_column("sections", "section_type")
