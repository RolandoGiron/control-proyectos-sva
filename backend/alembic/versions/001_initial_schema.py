"""initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-16 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables from scratch"""
    # Use IF NOT EXISTS to avoid errors if tables already exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Only create tables if they don't exist
    if 'areas' in existing_tables:
        return  # Tables already exist, skip

    # Create areas table
    op.create_table(
        'areas',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(7), nullable=False, server_default='#3B82F6'),
        sa.Column('icon', sa.String(10), nullable=False, server_default='📁'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_areas_name', 'areas', ['name'], unique=True)
    op.create_index('ix_areas_is_active', 'areas', ['is_active'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=True),
        sa.Column('telegram_chat_id', sa.BigInteger(), nullable=True, unique=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('role', sa.Enum('administrador', 'supervisor', 'analista', name='user_role'), nullable=False, server_default='analista'),
        sa.Column('area_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['area_id'], ['areas.id'], name='fk_users_area', ondelete='SET NULL'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_area_id', 'users', ['area_id'])
    op.create_index('ix_users_id', 'users', ['id'])

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('emoji_icon', sa.String(10), server_default='📁'),
        sa.Column('owner_id', sa.String(36), nullable=False),
        sa.Column('area_id', sa.String(36), nullable=True),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='fk_projects_owner', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['area_id'], ['areas.id'], name='fk_projects_area', ondelete='SET NULL'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_projects_owner_id', 'projects', ['owner_id'])
    op.create_index('ix_projects_area_id', 'projects', ['area_id'])
    op.create_index('ix_projects_is_archived', 'projects', ['is_archived'])
    op.create_index('ix_projects_id', 'projects', ['id'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('sin_empezar', 'en_curso', 'completado', name='task_status'), nullable=False, server_default='sin_empezar'),
        sa.Column('priority', sa.Enum('baja', 'media', 'alta', name='task_priority'), nullable=False, server_default='media'),
        sa.Column('responsible_id', sa.String(36), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('reminder_hours_before', sa.Integer(), nullable=True, server_default='24'),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_tasks_project', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['responsible_id'], ['users.id'], name='fk_tasks_responsible', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_tasks_created_by', ondelete='RESTRICT'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_tasks_project_id', 'tasks', ['project_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_responsible_id', 'tasks', ['responsible_id'])
    op.create_index('ix_tasks_deadline', 'tasks', ['deadline'])
    op.create_index('ix_tasks_created_by', 'tasks', ['created_by'])
    op.create_index('ix_tasks_id', 'tasks', ['id'])

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('task_id', sa.String(36), nullable=True),
        sa.Column('type', sa.Enum('nueva_tarea', 'recordatorio', 'completada', 'resumen_diario', 'resumen_semanal', 'cambio_estado', name='notification_type'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('read_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_notifications_user', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name='fk_notifications_task', ondelete='SET NULL'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_task_id', 'notifications', ['task_id'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])
    op.create_index('ix_notifications_sent_at', 'notifications', ['sent_at'])
    op.create_index('ix_notifications_read_at', 'notifications', ['read_at'])
    op.create_index('ix_notifications_id', 'notifications', ['id'])

    # Create telegram_link_codes table
    op.create_table(
        'telegram_link_codes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('code', sa.String(10), nullable=False, unique=True),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('used_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_telegram_link_codes_user', ondelete='CASCADE'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_telegram_link_codes_code', 'telegram_link_codes', ['code'], unique=True)
    op.create_index('ix_telegram_link_codes_user_id', 'telegram_link_codes', ['user_id'])
    op.create_index('ix_telegram_link_codes_expires_at', 'telegram_link_codes', ['expires_at'])
    op.create_index('ix_telegram_link_codes_id', 'telegram_link_codes', ['id'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('telegram_link_codes')
    op.drop_table('notifications')
    op.drop_table('tasks')
    op.drop_table('projects')
    op.drop_table('users')
    op.drop_table('areas')
