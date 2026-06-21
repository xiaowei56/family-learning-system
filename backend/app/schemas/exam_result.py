"""
考试成绩模块 Pydantic 模式

定义考试成绩 CRUD 及趋势分析接口的请求体和响应体数据结构与校验规则。
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ─── CRUD ────────────────────────────────────────────

class ExamResultCreate(BaseModel):
    """创建考试成绩请求体"""

    subject: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="科目名称",
        examples=["数学"],
    )
    exam_type: str = Field(
        ...,
        pattern=r"^(日常练习|周测|月考|期中|期末)$",
        description="考试类型：日常练习/周测/月考/期中/期末",
        examples=["月考"],
    )
    score: float = Field(
        ...,
        gt=0,
        description="得分",
        examples=[85.0],
    )
    total_score: float = Field(
        ...,
        gt=0,
        description="满分",
        examples=[100.0],
    )
    exam_date: date = Field(
        ...,
        description="考试日期",
        examples=["2026-06-15"],
    )
    notes: Optional[str] = Field(
        None,
        description="备注",
        examples=["第三章综合测试"],
    )

    @model_validator(mode="after")
    def validate_score_vs_total(self) -> "ExamResultCreate":
        """验证得分不超过满分。"""
        if self.score > self.total_score:
            raise ValueError("得分不能超过满分")
        return self


class ExamResultUpdate(BaseModel):
    """更新考试成绩请求体（全部可选）"""

    subject: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="科目名称",
        examples=["数学"],
    )
    exam_type: Optional[str] = Field(
        None,
        pattern=r"^(日常练习|周测|月考|期中|期末)$",
        description="考试类型：日常练习/周测/月考/期中/期末",
        examples=["月考"],
    )
    score: Optional[float] = Field(
        None,
        gt=0,
        description="得分",
        examples=[90.0],
    )
    total_score: Optional[float] = Field(
        None,
        gt=0,
        description="满分",
        examples=[100.0],
    )
    exam_date: Optional[date] = Field(
        None,
        description="考试日期",
        examples=["2026-06-20"],
    )
    notes: Optional[str] = Field(
        None,
        description="备注",
        examples=["第四章综合测试"],
    )


class ExamResultResponse(BaseModel):
    """考试成绩响应体"""

    id: str = Field(..., description="考试成绩 ID")
    user_id: str = Field(..., description="所属用户 ID")
    subject: str = Field(..., description="科目名称")
    exam_type: str = Field(..., description="考试类型")
    score: float = Field(..., description="得分")
    total_score: float = Field(..., description="满分")
    score_rate: float = Field(..., description="得分率")
    exam_date: date = Field(..., description="考试日期")
    notes: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    model_config = {"from_attributes": True}


# ─── 趋势分析 ────────────────────────────────────────

class TrendDataPoint(BaseModel):
    """趋势数据点"""

    date: date = Field(..., description="考试日期")
    score_rate: float = Field(..., description="得分率")
    score: float = Field(..., description="得分")
    total_score: float = Field(..., description="满分")
    exam_type: str = Field(..., description="考试类型")


class TrendSeries(BaseModel):
    """单科目趋势序列"""

    subject: str = Field(..., description="科目名称")
    data: list[TrendDataPoint] = Field(..., description="数据点列表")


class TrendResponse(BaseModel):
    """趋势图响应体"""

    series: list[TrendSeries] = Field(..., description="趋势序列列表")


# ─── 摘要统计 ────────────────────────────────────────

class LatestResult(BaseModel):
    """最新考试成绩摘要"""

    subject: str = Field(..., description="科目名称")
    score_rate: float = Field(..., description="得分率")
    exam_date: date = Field(..., description="考试日期")


class SummaryResponse(BaseModel):
    """摘要统计响应体"""

    subjects: list[str] = Field(..., description="科目列表")
    exam_types: list[str] = Field(..., description="考试类型列表")
    latest: list[LatestResult] = Field(..., description="各科目最新考试成绩")
