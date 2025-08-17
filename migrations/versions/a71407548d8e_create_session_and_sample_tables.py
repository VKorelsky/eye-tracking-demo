"""create session and sample tables

Revision ID: a71407548d8e
Revises:
Create Date: 2025-08-16 19:15:43.897096
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a71407548d8e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE session (
            id UUID NOT NULL,
            user_agent VARCHAR(1024) NOT NULL,
            sample_rate NUMERIC(10,2) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            duration DOUBLE PRECISION NOT NULL,
            PRIMARY KEY (id)
        )
    """
    )

    op.execute(
        """
        CREATE TABLE sample (
            session_id UUID NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            pos DOUBLE PRECISION NOT NULL,
            PRIMARY KEY (session_id, timestamp),
            FOREIGN KEY (session_id) REFERENCES session(id) ON DELETE CASCADE
        )
    """
    )

    # create an index on fetching samples by increasing time (older = first)
    op.execute(
        """
        CREATE INDEX idx_samples_session_time_desc
        ON sample (session_id, timestamp ASC)
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX idx_samples_session_time_desc")
    op.execute("DROP TABLE sample")
    op.execute("DROP TABLE session")
