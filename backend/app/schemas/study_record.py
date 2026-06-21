"""
学习记录与复习计划 Pydantic 模式

定义学习记录 CRUD 和复习管理的请求体/响应体数据结构与校验规则。
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class StudyRecordCreate(BaseModel):
    """创建学习记录请求体"""

    subject: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="科目名称",
        examples=["数学"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="学习标题",
        examples=["二次函数图像与性质"],
    )
    content: str = Field(
        ...,
        description="学习内容（支持富文本）",
        examples=["<p>二次函数 $y=ax^2+bx+c$ 的图像是一条抛物线...</p>"],
    )
    tags: list[str] = Field(
        default=[],
        description="知识点标签列表",
        examples=[["二次函数", "抛物线", "顶点式"]],
    )


class StudyRecordUpdate(BaseModel):
    """更新学习记录请求体"""

    subject: Optional[str] = Field(
        None,
        max_length=50,
        description="科目名称",
    )
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="学习标题",
    )
    content: Optional[str] = Field(
        None,
        description="学习内容（支持富文本）",
    )
    tags: Optional[list[str]] = Field(
        None,
        description="知识点标签列表",
    )


class StudyRecordResponse(BaseModel):
    """学习记录响应体"""

    id: str = Field(..., description="学习记录 ID")
    subject: str = Field(..., description="科目名称")
    title: str = Field(..., description="学习标题")
    content: str = Field(..., description="学习内容")
    tags: list[str] = Field(default=[], description="知识点标签")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    model_config = {"from_attributes": True}


class ReviewScheduleResponse(BaseModel):
    """复习安排响应体"""

    id: str = Field(..., description="复习记录 ID")
    study_record_id: str = Field(..., description="关联学习记录 ID")
    review_date: date = Field(..., description="计划复习日期")
    review_count: int = Field(..., description="第几次复习")
    status: str = Field(..., description="复习状态")
    speed_mode: str = Field(..., description="复习速度模式")

    model_config = {"from_attributes": True}


class ReviewRecordItem(BaseModel):
    """今日复习条目（含学习记录摘要信息）"""

    id: str = Field(..., description="复习记录 ID")
    study_record_id: str = Field(..., description="学习记录 ID")
    title: str = Field(..., description="学习标题")
    subject: str = Field(..., description="科目名称")
    review_count: int = Field(..., description="第几次复习")
    status: str = Field(..., description="复习状态")
    speed_mode: str = Field(..., description="复习速度模式")


class SubjectReviewGroup(BaseModel):
    """按科目分组的复习条目"""

    subject: str = Field(..., description="科目名称")
    records: list[ReviewRecordItem] = Field(..., description="该科目的复习列表")
    count: int = Field(..., description="该科目的复习数量")


class DailyReviewResponse(BaseModel):
    """每日复习查询响应"""

    subjects: list[SubjectReviewGroup] = Field(
        ..., description="按科目分组的复习列表"
    )
    total: int = Field(..., description="今日复习总数")


class SpeedUpdateRequest(BaseModel):
    """修改复习速度请求体"""

    speed_mode: str = Field(
        ...,
        pattern=r"^(fast|medium|slow)$",
        description="复习速度模式：fast（快速）/ medium（中等）/ slow（慢速）",
        examples=["fast"],
    )
