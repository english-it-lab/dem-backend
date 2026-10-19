"""add group status

Revision ID: ffc1f10ac39d
Revises: f9d10ab9bc1c
Create Date: 2026-05-10 22:33:38.633673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffc1f10ac39d'
down_revision: Union[str, Sequence[str], None] = 'f9d10ab9bc1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    group_status = sa.Enum('FORMING', 'PENDING', 'APPROVED', 'REJECTED', name='groupstatus')
    group_status.create(op.get_bind(), checkfirst=True)

    op.add_column('groups', sa.Column('status', group_status, server_default='FORMING', nullable=False))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('groups', 'status')

    group_status = sa.Enum('FORMING', 'PENDING', 'APPROVED', 'REJECTED', name='groupstatus')
    group_status.drop(op.get_bind(), checkfirst=True)
