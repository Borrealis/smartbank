"""convert task status to enum

Revision ID: a6f231b92541
Revises: 2f66a1847a92
Create Date: 2026-09-27 20:04:32.444953
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a6f231b92541"
down_revision: Union[str, Sequence[str], None] = "2f66a1847a92"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

task_status = postgresql.ENUM(
    "PROCESSING",
    "COMPLETED",
    "FAILED",
    name="task_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute("UPDATE tasks SET status = 'PROCESSING' WHERE status = 'PENDING'")
    task_status.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "tasks",
        "status",
        existing_type=sa.String(),
        type_=task_status,
        existing_nullable=False,
        postgresql_using="status::task_status",
    )


def downgrade() -> None:
    op.alter_column(
        "tasks",
        "status",
        existing_type=task_status,
        type_=sa.String(),
        existing_nullable=False,
        postgresql_using="status::text",
    )
    task_status.drop(op.get_bind(), checkfirst=True)
