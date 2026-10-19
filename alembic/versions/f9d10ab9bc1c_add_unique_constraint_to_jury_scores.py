"""add unique constraint to jury_scores

Revision ID: f9d10ab9bc1c
Revises: 73887235ae3c
Create Date: 2025-12-15 20:29:44.678949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9d10ab9bc1c'
down_revision: Union[str, Sequence[str], None] = '73887235ae3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique constraint on jury_id + participant_id
    op.create_unique_constraint(
        'uq_jury_participant_score',
        'jury_scores',
        ['jury_id', 'participant_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove unique constraint
    op.drop_constraint('uq_jury_participant_score', 'jury_scores', type_='unique')
