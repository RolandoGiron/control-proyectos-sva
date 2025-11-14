"""add_areas_table

Revision ID: 4cf674784ecd
Revises: 9f5bf52fe18f
Create Date: 2025-11-13 23:07:13.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cf674784ecd'
down_revision: Union[str, None] = '9f5bf52fe18f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Verificar si la tabla areas existe, si no existe, crearla
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if 'areas' not in inspector.get_table_names():
        # Crear tabla areas
        op.create_table(
            'areas',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('color', sa.String(length=7), nullable=False, server_default='#3B82F6'),
            sa.Column('icon', sa.String(length=10), nullable=False, server_default='📁'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id'),
            mysql_collate='utf8mb4_unicode_ci',
            mysql_default_charset='utf8mb4',
            mysql_engine='InnoDB'
        )

        # Crear índices
        op.create_index(op.f('ix_areas_name'), 'areas', ['name'], unique=True)
        op.create_index(op.f('ix_areas_is_active'), 'areas', ['is_active'], unique=False)


def downgrade() -> None:
    # Eliminar tabla areas solo si existe
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if 'areas' in inspector.get_table_names():
        op.drop_index(op.f('ix_areas_is_active'), table_name='areas')
        op.drop_index(op.f('ix_areas_name'), table_name='areas')
        op.drop_table('areas')
