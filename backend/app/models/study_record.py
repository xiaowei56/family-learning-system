"""
学习记录与复习排期模型

存储日常学习笔记和基于艾宾浩斯遗忘曲线的复习排期。
"""

import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class StudyRecord(Base):
    """学习记录表"""

    __tablename__ = "study_records"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="学习记录唯一标识",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户 ID",
    )
    subject = Column(
        String(50),
        nullable=False,
        comment="科目名称",
    )
    title = Column(
        String(200),
        nullable=False,
        comment="学习标题",
    )
    content = Column(
        Text,
        nullable=False,
        comment="学习内容（支持富文本）",
    )
    tags = Column(
        JSON,
        nullable=False,
        default=list,
        comment="知识点标签列表",
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
    user = relationship("User", backref="study_records", lazy="joined")
    reviews = relationship(
        "ReviewSchedule",
        back_populates="study_record",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return (
            f"<StudyRecord(id={self.id}, title='{self.title}', "
            f"subject='{self.subject}')>"
        )


class ReviewSchedule(Base):
    """复习排期表"""

    __tablename__ = "review_schedules"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="复习记录唯一标识",
    )
    study_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("study_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联学习记录 ID",
    )
    review_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="计划复习日期",
    )
    review_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="第几次复习（从 1 开始）",
    )
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="复习状态：pending（待复习）/ done（已完成）/ mastered（已掌握）",
    )
    speed_mode = Column(
        String(10),
        nullable=False,
        default="medium",
        comment="复习速度模式：fast（快速）/ medium（中等）/ slow（慢速）",
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
    study_record = relationship("StudyRecord", back_populates="reviews")

    def __repr__(self) -> str:
        return (
            f"<ReviewSchedule(id={self.id}, record_id={self.study_record_id}, "
            f"date={self.review_date}, status='{self.status}')>"
        )
