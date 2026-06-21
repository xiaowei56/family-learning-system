"""
试卷整理模块 Pydantic 模式

定义试卷上传、查询、笔迹擦除、标注等接口的请求/响应数据结构。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── 试卷 CRUD ─────────────────────────────────────────

class ExamPaperCreate(BaseModel):
    """创建试卷请求体"""

    student_id: Optional[str] = Field(
        None,
        description="所属学生 ID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    subject: str = Field(..., max_length=50, description="科目名称")
    title: str = Field(..., max_length=200, description="试卷标题")
    exam_type: Optional[str] = Field(None, max_length=50, description="考试类型")
    exam_date: Optional[str] = Field(None, description="考试日期")
    image_path: str = Field(..., description="原始图片 MinIO 路径")
    page_count: Optional[int] = Field(1, ge=1, description="页数")


class ExamPaperUpdate(BaseModel):
    """更新试卷请求体（全部可选）"""

    title: Optional[str] = Field(None, max_length=200, description="试卷标题")
    exam_type: Optional[str] = Field(None, max_length=50, description="考试类型")
    exam_date: Optional[str] = Field(None, description="考试日期")
    subject: Optional[str] = Field(None, max_length=50, description="科目")
    status: Optional[str] = Field(None, pattern=r"^(uploaded|ocr_done|cleaned|annotated)$", description="状态")


class ExamPaperResponse(BaseModel):
    """试卷响应体"""

    id: str = Field(..., description="试卷 ID")
    user_id: str = Field(..., description="用户 ID")
    student_id: Optional[str] = Field(None, description="所属学生 ID")
    subject: str = Field(..., description="科目")
    title: str = Field(..., description="标题")
    exam_type: Optional[str] = Field(None, description="考试类型")
    exam_date: Optional[str] = Field(None, description="考试日期")
    original_image_path: str = Field(..., description="原始图片路径")
    clean_image_path: Optional[str] = Field(None, description="洁净版图片路径")
    ocr_text: Optional[str] = Field(None, description="OCR 文本")
    page_count: int = Field(..., description="页数")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class ExamPaperListResponse(BaseModel):
    """试卷列表响应体"""

    items: list[ExamPaperResponse] = Field(..., description="试卷列表")
    total: int = Field(..., description="总数")


# ─── 笔迹擦除 ──────────────────────────────────────────

class EraseHandwritingRequest(BaseModel):
    """笔迹擦除请求体"""

    paper_id: str = Field(..., description="试卷 ID")
    regions: list[dict] = Field(default_factory=list, description="指定擦除区域 [{x,y,w,h}]，空则全图")


class EraseHandwritingResponse(BaseModel):
    """笔迹擦除响应体"""

    clean_image_path: str = Field(..., description="洁净版图片路径")
    status: str = Field(..., description="处理状态")


# ─── 试卷标注 ──────────────────────────────────────────

class PaperAnnotationCreate(BaseModel):
    """创建标注请求体"""

    annotation_type: str = Field(
        ..., pattern=r"^(highlight|underline|mark|text)$",
        description="标注类型",
    )
    position: dict = Field(..., description="位置信息")
    content: Optional[str] = Field(None, description="标注内容")
    color: Optional[str] = Field("#ff0000", description="标注颜色")


class PaperAnnotationResponse(BaseModel):
    """标注响应体"""

    id: str = Field(..., description="标注 ID")
    paper_id: str = Field(..., description="试卷 ID")
    annotation_type: str = Field(..., description="标注类型")
    position: dict = Field(..., description="位置信息")
    content: Optional[str] = Field(None, description="标注内容")
    color: Optional[str] = Field(None, description="标注颜色")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}
