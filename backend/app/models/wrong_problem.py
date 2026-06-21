"""
错题模型

存储 OCR 识别后的错题记录，包括原题文本、答案、AI 评估结果和解题过程。
"""

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class WrongProblem(Base):
    """错题表"""

    __tablename__ = "wrong_problems"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="错题唯一标识",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属用户 ID",
    )
    subject = Column(
        String(50),
        nullable=False,
        comment="科目名称",
    )
    knowledge_point = Column(
        String(200),
        nullable=False,
        comment="知识点标签",
    )
    problem_text = Column(
        Text,
        nullable=False,
        comment="题目原文（OCR 识别结果或手动录入）",
    )
    student_answer = Column(
        Text,
        nullable=True,
        comment="学生作答内容",
    )
    correct_answer = Column(
        Text,
        nullable=True,
        comment="正确答案",
    )
    ai_evaluation = Column(
        Text,
        nullable=True,
        comment="AI 评估结果（对错判断 + 错误原因分析）",
    )
    is_correct = Column(
        Integer,
        nullable=True,
        comment="是否正确：1=正确，0=错误，NULL=待评估",
    )
    solution = Column(
        Text,
        nullable=True,
        comment="AI 生成的解题步骤（含公式/图示说明）",
    )
    image_path = Column(
        String(500),
        nullable=True,
        comment="原始图片在 MinIO 中的存储路径",
    )
    difficulty = Column(
        Integer,
        default=1,
        comment="难度等级：1=简单，2=中等，3=困难",
    )
    wrong_count = Column(
        Integer,
        default=1,
        nullable=False,
        comment="累计错误次数",
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
    user = relationship("User", backref="wrong_problems")

    def __repr__(self) -> str:
        return (
            f"<WrongProblem(id={self.id}, subject='{self.subject}', "
            f"point='{self.knowledge_point}')>"
        )
