"""
试卷整理模型

存储上传的试卷图片、笔迹擦除后的洁净版、以及题目标注信息。
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ExamPaper(Base):
    """试卷表"""

    __tablename__ = "exam_papers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="试卷唯一标识",
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
        comment="科目名称",
    )
    title = Column(
        String(200),
        nullable=False,
        comment="试卷标题",
    )
    exam_type = Column(
        String(50),
        nullable=True,
        comment="考试类型：日常练习/周测/月考/期中/期末",
    )
    exam_date = Column(
        String(20),
        nullable=True,
        comment="考试日期",
    )
    original_image_path = Column(
        String(500),
        nullable=False,
        comment="原始试卷图片在 MinIO 中的路径",
    )
    clean_image_path = Column(
        String(500),
        nullable=True,
        comment="笔迹擦除后的洁净版图片路径",
    )
    ocr_text = Column(
        Text,
        nullable=True,
        comment="整卷 OCR 识别文本",
    )
    page_count = Column(
        Integer,
        default=1,
        nullable=False,
        comment="试卷页数",
    )
    status = Column(
        String(20),
        nullable=False,
        default="uploaded",
        comment="状态：uploaded(已上传)/ocr_done(已识别)/cleaned(已擦除)/annotated(已标注)",
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
    user = relationship("User", backref="exam_papers")
    annotations = relationship(
        "PaperAnnotation",
        back_populates="exam_paper",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return (
            f"<ExamPaper(id={self.id}, title='{self.title}', "
            f"subject='{self.subject}')>"
        )


class PaperAnnotation(Base):
    """试卷标注表"""

    __tablename__ = "paper_annotations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="标注唯一标识",
    )
    paper_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exam_papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联试卷 ID",
    )
    annotation_type = Column(
        String(50),
        nullable=False,
        comment="标注类型：highlight(高亮)/underline(下划线)/mark(标记)/text(文字备注)",
    )
    position = Column(
        JSON,
        nullable=False,
        comment="标注位置信息：{x, y, width, height} 或 {start, end}",
    )
    content = Column(
        Text,
        nullable=True,
        comment="标注内容（文字备注时使用）",
    )
    color = Column(
        String(20),
        nullable=True,
        default="#ff0000",
        comment="标注颜色",
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
    exam_paper = relationship("ExamPaper", back_populates="annotations")

    def __repr__(self) -> str:
        return (
            f"<PaperAnnotation(id={self.id}, paper_id={self.paper_id}, "
            f"type='{self.annotation_type}')>"
        )
