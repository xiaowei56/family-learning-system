"""
举一反三、薄弱点分析与练习试卷模型

存储 LLM 生成的相似题目、薄弱点分析结果、练习试卷和学习建议。
"""

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SimilarProblem(Base):
    """相似题目表"""

    __tablename__ = "similar_problems"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="相似题唯一标识",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属用户 ID",
    )
    source_problem_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wrong_problems.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="来源错题 ID",
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
        comment="相似题目文本",
    )
    answer = Column(
        Text,
        nullable=True,
        comment="答案",
    )
    solution = Column(
        Text,
        nullable=True,
        comment="解题过程（分步骤）",
    )
    difficulty = Column(
        Integer,
        default=1,
        comment="难度等级：1=简单，2=中等，3=困难",
    )
    is_practiced = Column(
        Integer,
        default=0,
        comment="是否已练习：0=未练习，1=已练习",
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
    user = relationship("User", backref="similar_problems")

    def __repr__(self) -> str:
        return (
            f"<SimilarProblem(id={self.id}, subject='{self.subject}', "
            f"point='{self.knowledge_point}')>"
        )


class WeakPoint(Base):
    """薄弱点分析结果表"""

    __tablename__ = "weak_points"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="薄弱点记录唯一标识",
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
        comment="知识点名称",
    )
    mastery_level = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="掌握程度：0.0~1.0，越低越薄弱",
    )
    wrong_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="该知识点错误次数",
    )
    total_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="该知识点总题数",
    )
    suggestion = Column(
        Text,
        nullable=True,
        comment="学习建议",
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
    user = relationship("User", backref="weak_points")

    def __repr__(self) -> str:
        return (
            f"<WeakPoint(id={self.id}, subject='{self.subject}', "
            f"point='{self.knowledge_point}', mastery={self.mastery_level})>"
        )


class PracticePaper(Base):
    """练习试卷表"""

    __tablename__ = "practice_papers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="练习试卷唯一标识",
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
    title = Column(
        String(200),
        nullable=False,
        comment="试卷标题",
    )
    questions = Column(
        JSON,
        nullable=False,
        default=list,
        comment="题目列表：[{problem, answer, solution, knowledge_point, difficulty}, ...]",
    )
    target_points = Column(
        JSON,
        nullable=True,
        default=list,
        comment="针对的薄弱知识点列表",
    )
    total_questions = Column(
        Integer,
        default=0,
        nullable=False,
        comment="题目总数",
    )
    difficulty_distribution = Column(
        JSON,
        nullable=True,
        comment="难度分布：{simple: N, medium: N, hard: N}",
    )
    status = Column(
        String(20),
        nullable=False,
        default="generated",
        comment="状态：generated(已生成)/started(已开始)/completed(已完成)",
    )
    score = Column(
        Float,
        nullable=True,
        comment="练习得分率",
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
    user = relationship("User", backref="practice_papers")

    def __repr__(self) -> str:
        return (
            f"<PracticePaper(id={self.id}, title='{self.title}', "
            f"subject='{self.subject}', questions={self.total_questions})>"
        )


class LearningAdvice(Base):
    """学习建议表"""

    __tablename__ = "learning_advices"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="学习建议唯一标识",
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
        nullable=True,
        comment="科目名称（空表示综合建议）",
    )
    overall_diagnosis = Column(
        Text,
        nullable=True,
        comment="总体诊断",
    )
    study_plan = Column(
        Text,
        nullable=True,
        comment="学习计划",
    )
    weak_points_detail = Column(
        JSON,
        nullable=True,
        default=list,
        comment="薄弱点详情列表",
    )
    suggestions = Column(
        JSON,
        nullable=True,
        default=list,
        comment="专项建议列表",
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
    user = relationship("User", backref="learning_advices")

    def __repr__(self) -> str:
        return f"<LearningAdvice(id={self.id}, subject='{self.subject}')>"
