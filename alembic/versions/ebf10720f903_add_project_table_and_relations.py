"""add project table and relations

Revision ID: ebf10720f903
Revises: be9b90db34e9
Create Date: 2025-05-30 18:44:17.656669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ebf10720f903'
down_revision: Union[str, None] = 'be9b90db34e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the enum
priority_enum = postgresql.ENUM('low', 'medium', 'high', name='prioritylevel')


def upgrade() -> None:
    # Create enum type
    priority_enum.create(op.get_bind())

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)

    # Alter tasks table
    op.add_column('tasks', sa.Column('priority', sa.Enum('low', 'medium', 'high', name='prioritylevel'), nullable=False, server_default='medium'))
    op.add_column('tasks', sa.Column('deadline', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('tasks', sa.Column('project_id', sa.Integer(), nullable=True))

    op.alter_column('tasks', 'description',
               existing_type=sa.VARCHAR(length=500),
               type_=sa.Text(),
               existing_nullable=True)
    op.alter_column('tasks', 'is_completed',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('tasks', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))

    op.create_foreign_key(None, 'tasks', 'projects', ['project_id'], ['id'])
    op.create_foreign_key(None, 'tasks', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # Drop FKs
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_constraint(None, 'tasks', type_='foreignkey')

    # Revert task column changes
    op.alter_column('tasks', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('now()'))
    op.alter_column('tasks', 'is_completed',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('tasks', 'description',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=500),
               existing_nullable=True)

    op.drop_column('tasks', 'project_id')
    op.drop_column('tasks', 'user_id')
    op.drop_column('tasks', 'deadline')
    op.drop_column('tasks', 'priority')

    # Drop projects table
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')

    # Drop enum type
    priority_enum.drop(op.get_bind())
