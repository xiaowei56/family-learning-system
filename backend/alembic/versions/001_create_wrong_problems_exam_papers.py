"""create wrong_problems, exam_papers, paper_annotations,
     similar_problems, weak_points, practice_papers, learning_advices tables

Revision ID: 001
Revises:
Create Date: 2026-06-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── wrong_problems 错题表 ───────────────────────
    op.create_table(
        "wrong_problems",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), index=True
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("subject", sa.String(50), nullable=False),
        sa.Column("knowledge_point", sa.String(200), nullable=False),
        sa.Column("problem_text", sa.Text, nullable=False),
        sa.Column("student_answer", sa.Text, nullable=True),
        sa.Column("correct_answer", sa.Text, nullable=True),
        sa.Column("ai_evaluation", sa.Text, nullable=True),
        sa.Column("is_correct", sa.Integer, nullable=True),
        sa.Column("solution", sa.Text, nullable=True),
        sa.Column("image_path", sa.String(500), nullable=True),
        sa.Column("difficulty", sa.Integer, server_default=sa.text("1"), nullable=False),
        sa.Column("wrong_count", sa.Integer, server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── exam_papers 试卷表 ──────────────────────────
    op.create_table(
        "exam_papers",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), index=True
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("subject", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("exam_type", sa.String(50), nullable=True),
        sa.Column("exam_date", sa.String(20), nullable=True),
        sa.Column("original_image_path", sa.String(500), nullable=False),
        sa.Column("clean_image_path", sa.String(500), nullable=True),
        sa.Column("ocr_text", sa.Text, nullable=True),
        sa.Column("page_count", sa.Integer, server_default=sa.text("1"), nullable=False),
        sa.Column("status", sa.String(20), server_default=sa.text("'uploaded'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── paper_annotations 试卷标注表 ────────────────
    op.create_table(
        "paper_annotations",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), index=True
        ),
        sa.Column("paper_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exam_papers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("annotation_type", sa.String(50), nullable=False),
        sa.Column("position", postgresql.JSON, nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("color", sa.String(20), server_default=sa.text("'#ff0000'"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── similar_problems 相似题表 ────────────────────
    op.create_table(
        "similar_problems",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("source_problem_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wrong_problems.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("subject", sa.String(50), nullable=False),
        sa.Column("knowledge_point", sa.String(200), nullable=False),
        sa.Column("problem_text", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=True),
        sa.Column("solution", sa.Text, nullable=True),
        sa.Column("difficulty", sa.Integer, server_default=sa.text("1"), nullable=False),
        sa.Column("is_practiced", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── weak_points 薄弱点分析表 ─────────────────────
    op.create_table(
        "weak_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("subject", sa.String(50), nullable=False),
        sa.Column("knowledge_point", sa.String(200), nullable=False),
        sa.Column("mastery_level", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("wrong_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("total_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("suggestion", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── practice_papers 练习试卷表 ───────────────────
    op.create_table(
        "practice_papers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("subject", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("questions", postgresql.JSON, nullable=False),
        sa.Column("target_points", postgresql.JSON, nullable=True),
        sa.Column("total_questions", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("difficulty_distribution", postgresql.JSON, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'generated'")),
        sa.Column("score", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── learning_advices 学习建议表 ──────────────────
    op.create_table(
        "learning_advices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("subject", sa.String(50), nullable=True),
        sa.Column("overall_diagnosis", sa.Text, nullable=True),
        sa.Column("study_plan", sa.Text, nullable=True),
        sa.Column("weak_points_detail", postgresql.JSON, nullable=True),
        sa.Column("suggestions", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("learning_advices")
    op.drop_table("practice_papers")
    op.drop_table("weak_points")
    op.drop_table("similar_problems")
    op.drop_table("paper_annotations")
    op.drop_table("exam_papers")
    op.drop_table("wrong_problems")
