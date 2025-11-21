"""add_is_archived_to_tasks

Revision ID: 9b7ce5d38f19
Revises: 001_initial_schema
Create Date: 2025-11-21 00:35:31.827285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b7ce5d38f19'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_archived column to tasks table"""
    # Check if column already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('tasks')]

    if 'is_archived' not in columns:
        op.add_column('tasks', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='0'))
        op.create_index('ix_tasks_is_archived', 'tasks', ['is_archived'])


def downgrade() -> None:
    """Remove is_archived column from tasks table"""
    op.drop_index('ix_tasks_is_archived', 'tasks')
    op.drop_column('tasks', 'is_archived')
