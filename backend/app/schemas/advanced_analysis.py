"""
举一反三、薄弱点分析与练习试卷 Pydantic 模式

定义相似题目生成、薄弱点分析、智能出卷和学习诊断的数据结构。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── 举一反三 ──────────────────────────────────────────

class SimilarProblemGenerateRequest(BaseModel):
    """生成相似题请求体"""

    source_problem_id: Optional[str] = Field(None, description="来源错题 ID")
    subject: str = Field(..., max_length=50, description="科目")
    knowledge_point: str = Field(..., max_length=200, description="知识点")
    problem_text: str = Field(..., description="原题文本")


class SimilarProblemGenerateResponse(BaseModel):
    """生成相似题响应体"""

    problem: str = Field(..., description="生成的相似题")
    answer: str = Field(..., description="答案")
    solution: str = Field(..., description="解题过程")
    difficulty: int = Field(..., description="难度等级")


class SimilarProblemResponse(BaseModel):
    """相似题响应体"""

    id: str = Field(..., description="相似题 ID")
    subject: str = Field(..., description="科目")
    knowledge_point: str = Field(..., description="知识点")
    problem_text: str = Field(..., description="相似题目")
    answer: Optional[str] = Field(None, description="答案")
    solution: Optional[str] = Field(None, description="解题过程")
    difficulty: int = Field(..., description="难度")
    is_practiced: int = Field(..., description="是否已练习")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class SimilarProblemListResponse(BaseModel):
    """相似题列表响应体"""

    items: list[SimilarProblemResponse] = Field(..., description="相似题列表")
    total: int = Field(..., description="总数")


# ─── 薄弱点分析 ────────────────────────────────────────

class WeakPointResponse(BaseModel):
    """薄弱点响应体"""

    id: str = Field(..., description="记录 ID")
    subject: str = Field(..., description="科目")
    knowledge_point: str = Field(..., description="知识点")
    mastery_level: float = Field(..., description="掌握程度")
    wrong_count: int = Field(..., description="错误次数")
    total_count: int = Field(..., description="总题数")
    suggestion: Optional[str] = Field(None, description="学习建议")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class WeakPointAnalysisResponse(BaseModel):
    """综合薄弱点分析响应体"""

    weak_points: list[WeakPointResponse] = Field(..., description="薄弱点列表")
    overall_diagnosis: str = Field(..., description="总体诊断")
    study_plan: str = Field(..., description="学习计划")


# ─── 练习试卷 ──────────────────────────────────────────

class PracticePaperGenerateRequest(BaseModel):
    """生成练习试卷请求体"""

    subject: str = Field(..., max_length=50, description="科目")
    weak_points: list[str] = Field(..., description="针对的薄弱知识点列表")
    question_count: int = Field(10, ge=1, le=50, description="题目数量")


class PracticePaperResponse(BaseModel):
    """练习试卷响应体"""

    id: str = Field(..., description="试卷 ID")
    subject: str = Field(..., description="科目")
    title: str = Field(..., description="标题")
    questions: list = Field(..., description="题目列表")
    target_points: list = Field(..., description="针对知识点")
    total_questions: int = Field(..., description="题目总数")
    difficulty_distribution: Optional[dict] = Field(None, description="难度分布")
    status: str = Field(..., description="状态")
    score: Optional[float] = Field(None, description="得分率")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class PracticePaperListResponse(BaseModel):
    """练习试卷列表响应体"""

    items: list[PracticePaperResponse] = Field(..., description="试卷列表")
    total: int = Field(..., description="总数")


# ─── 学习诊断报告 ─────────────────────────────────────

class LearningAdviceResponse(BaseModel):
    """学习建议响应体"""

    id: str = Field(..., description="建议 ID")
    subject: Optional[str] = Field(None, description="科目")
    overall_diagnosis: Optional[str] = Field(None, description="总体诊断")
    study_plan: Optional[str] = Field(None, description="学习计划")
    weak_points_detail: list = Field(default_factory=list, description="薄弱点详情")
    suggestions: list = Field(default_factory=list, description="专项建议")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}
