"""
用户模型

存储家长和学生账号的认证信息与基本资料。
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """用户账号表"""

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="用户唯一标识",
    )
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="用户名（登录用）",
    )
    hashed_password = Column(
        String(255),
        nullable=False,
        comment="bcrypt 加密后的密码哈希",
    )
    role = Column(
        Enum("parent", "student", name="user_role"),
        nullable=False,
        default="parent",
        comment="用户角色：parent（家长）/ student（学生）",
    )
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="账号是否激活",
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

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
