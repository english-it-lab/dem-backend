"""make email field unique and non-nullable

Revision ID: 1bc6b59ad6ca
Revises: ffc1f10ac39d
Create Date: 2026-05-13 21:08:05.281068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bc6b59ad6ca'
down_revision: Union[str, Sequence[str], None] = 'ffc1f10ac39d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('people', 'email',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.create_unique_constraint(None, 'people', ['email'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'people', type_='unique')
    op.alter_column('people', 'email',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
