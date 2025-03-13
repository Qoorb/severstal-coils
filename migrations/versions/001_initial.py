"""initial

Revision ID: 001
Revises:
Create Date: 2024-03-13 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "coils",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("length", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_coils_id"), "coils", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_coils_id"), table_name="coils")
    op.drop_table("coils")
