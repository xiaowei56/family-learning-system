"""
考试成绩模型

记录每次考试/练习的得分与得分率，支持趋势分析和多科目对比。
"""

import uuid
import enum

from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ExamType(str, enum.Enum):
    """考试类型枚举"""
    DAILY = "日常练习"
    WEEKLY = "周测"
    MONTHLY = "月考"
    MIDTERM = "期中"
    FINAL = "期末"


class ExamResult(Base):
    """考试成绩表"""

    __tablename__ = "exam_results"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="考试成绩唯一标识",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属用户 ID",
    )
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="所属学生 ID",
    )
    subject = Column(
        String(50),
        nullable=False,
        comment="科目名称，如 数学、物理、语文",
    )
    exam_type = Column(
        Enum(ExamType, name="exam_type"),
        nullable=False,
        comment="考试类型：日常练习/周测/月考/期中/期末",
    )
    score = Column(
        Float,
        nullable=False,
        comment="得分",
    )
    total_score = Column(
        Float,
        nullable=False,
        comment="满分",
    )
    score_rate = Column(
        Float,
        nullable=False,
        comment="得分率（自动计算：score / total_score）",
    )
    exam_date = Column(
        Date,
        nullable=False,
        comment="考试日期",
    )
    notes = Column(
        Text,
        nullable=True,
        comment="备注",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="最后更新时间",
    )

    # ─── 关系 ────────────────────────────────────────
    user = relationship("User", backref="exam_results")

    def __repr__(self) -> str:
        return (
            f"<ExamResult(id={self.id}, subject='{self.subject}', "
            f"score={self.score}/{self.total_score})>"
        )
