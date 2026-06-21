"""
学生档案模型

一个家长账号可管理多个学生档案，每个学生独立配置年级和科目。
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Student(Base):
    """学生档案表"""

    __tablename__ = "students"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="学生档案唯一标识",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属家长用户 ID",
    )
    name = Column(
        String(50),
        nullable=False,
        comment="学生姓名",
    )
    grade_level = Column(
        String(10),
        nullable=False,
        comment="年级：小学 / 初中 / 高中",
    )
    avatar = Column(
        Text,
        nullable=True,
        comment="头像 URL（MinIO 存储地址）",
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
    user = relationship("User", backref="students")
    study_records = relationship("StudyRecord", backref="student", lazy="dynamic")
    review_schedules = relationship("ReviewSchedule", backref="student", lazy="dynamic")
    exam_results = relationship("ExamResult", backref="student", lazy="dynamic")
    wrong_problems = relationship("WrongProblem", backref="student", lazy="dynamic")
    exam_papers = relationship("ExamPaper", backref="student", lazy="dynamic")
    similar_problems = relationship("SimilarProblem", backref="student", lazy="dynamic")
    weak_points = relationship("WeakPoint", backref="student", lazy="dynamic")
    practice_papers = relationship("PracticePaper", backref="student", lazy="dynamic")
    learning_advices = relationship("LearningAdvice", backref="student", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.name}', grade='{self.grade_level}')>"
