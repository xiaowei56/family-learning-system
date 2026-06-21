"""add student_id column to all data tables

Revision ID: 002
Revises: 001
Create Date: 2026-06-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── study_records ─────────────────────────────────
    op.add_column(
        "study_records",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True),
    )

    # ─── review_schedules ──────────────────────────────
    op.add_column(
        "review_schedules",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True),
    )

    # ─── exam_results ──────────────────────────────────
    op.add_column(
        "exam_results",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True),
    )

    # ─── wrong_problems ────────────────────────────────
    op.add_column(
        "wrong_problems",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True),
    )

    # ─── exam_papers ───────────────────────────────────
    op.add_column(
        "exam_papers",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True),
    )

    # ─── similar_problems ──────────────────────────────
    op.add_column(
        "similar_problems",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True),
    )

    # ─── weak_points ───────────────────────────────────
    op.add_column(
        "weak_points",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True),
    )

    # ─── practice_papers ───────────────────────────────
    op.add_column(
        "practice_papers",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True),
    )

    # ─── learning_advices ──────────────────────────────
    op.add_column(
        "learning_advices",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=True, index=True),
    )


def downgrade() -> None:
    op.drop_column("learning_advices", "student_id")
    op.drop_column("practice_papers", "student_id")
    op.drop_column("weak_points", "student_id")
    op.drop_column("similar_problems", "student_id")
    op.drop_column("exam_papers", "student_id")
    op.drop_column("wrong_problems", "student_id")
    op.drop_column("exam_results", "student_id")
    op.drop_column("review_schedules", "student_id")
    op.drop_column("study_records", "student_id")
