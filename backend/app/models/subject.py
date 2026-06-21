"""
科目与用户-科目关联模型

预设各年级可选科目，支持用户按需配置学习科目。
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ─── 多对多关联表：用户 ↔ 科目 ─────────────────────
class UserSubject(Base):
    """用户-科目关联表"""

    __tablename__ = "user_subjects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="关联记录唯一标识",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户 ID",
    )
    subject_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="科目 ID",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    def __repr__(self) -> str:
        return f"<UserSubject(user_id={self.user_id}, subject_id={self.subject_id})>"


class Subject(Base):
    """科目字典表"""

    __tablename__ = "subjects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="科目唯一标识",
    )
    name = Column(
        String(20),
        unique=True,
        nullable=False,
        comment="科目名称，如 数学、物理、语文",
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    # ─── 关系 ────────────────────────────────────────
    users = relationship("UserSubject", backref="subject", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name='{self.name}')>"
