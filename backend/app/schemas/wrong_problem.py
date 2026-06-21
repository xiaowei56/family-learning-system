"""
错题模块 Pydantic 模式

定义错题 CRUD、OCR 识别、AI 评估和解题过程的请求/响应数据结构。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── OCR 识别 ──────────────────────────────────────────

class OCRRequest(BaseModel):
    """OCR 识别请求体"""

    image_path: str = Field(..., description="MinIO 中的图片路径", examples=["papers/abc123.jpg"])


class OCRResponse(BaseModel):
    """OCR 识别响应体"""

    text: str = Field(..., description="识别文本")
    confidence: float = Field(default=0.0, description="识别置信度")
    image_path: str = Field(..., description="图片路径")


# ─── AI 评估 ───────────────────────────────────────────

class AIEvaluationRequest(BaseModel):
    """AI 评估请求体"""

    problem_text: str = Field(..., description="题目原文", examples=["计算 2+3×4 的值"])
    student_answer: str = Field(..., description="学生作答", examples=["20"])
    subject: str = Field(..., max_length=50, description="科目", examples=["数学"])


class AIEvaluationResponse(BaseModel):
    """AI 评估响应体"""

    is_correct: bool = Field(..., description="是否回答正确")
    evaluation: str = Field(..., description="评估分析")
    correct_answer: Optional[str] = Field(None, description="正确答案")


# ─── 解题过程 ──────────────────────────────────────────

class SolutionRequest(BaseModel):
    """解题过程请求体"""

    problem_text: str = Field(..., description="题目原文")
    subject: str = Field(..., max_length=50, description="科目")
    knowledge_point: str = Field(..., max_length=200, description="知识点")


class SolutionResponse(BaseModel):
    """解题过程响应体"""

    solution: str = Field(..., description="解题步骤")
    approach: str = Field(..., description="解题思路分析")


# ─── 错题 CRUD ─────────────────────────────────────────

class WrongProblemCreate(BaseModel):
    """创建错题请求体"""

    student_id: Optional[str] = Field(
        None,
        description="所属学生 ID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    subject: str = Field(..., max_length=50, description="科目名称")
    knowledge_point: str = Field(..., max_length=200, description="知识点标签")
    problem_text: str = Field(..., description="题目原文")
    student_answer: Optional[str] = Field(None, description="学生作答")
    correct_answer: Optional[str] = Field(None, description="正确答案")
    ai_evaluation: Optional[str] = Field(None, description="AI 评估结果")
    is_correct: Optional[int] = Field(None, description="是否正确")
    solution: Optional[str] = Field(None, description="解题步骤")
    image_path: Optional[str] = Field(None, description="图片路径")
    difficulty: Optional[int] = Field(1, ge=1, le=3, description="难度等级")


class WrongProblemUpdate(BaseModel):
    """更新错题请求体（全部可选）"""

    knowledge_point: Optional[str] = Field(None, max_length=200, description="知识点标签")
    student_answer: Optional[str] = Field(None, description="学生作答")
    correct_answer: Optional[str] = Field(None, description="正确答案")
    ai_evaluation: Optional[str] = Field(None, description="AI 评估结果")
    is_correct: Optional[int] = Field(None, description="是否正确")
    solution: Optional[str] = Field(None, description="解题步骤")
    difficulty: Optional[int] = Field(None, ge=1, le=3, description="难度等级")


class WrongProblemResponse(BaseModel):
    """错题响应体"""

    id: str = Field(..., description="错题 ID")
    user_id: str = Field(..., description="用户 ID")
    student_id: Optional[str] = Field(None, description="所属学生 ID")
    subject: str = Field(..., description="科目")
    knowledge_point: str = Field(..., description="知识点")
    problem_text: str = Field(..., description="题目原文")
    student_answer: Optional[str] = Field(None, description="学生作答")
    correct_answer: Optional[str] = Field(None, description="正确答案")
    ai_evaluation: Optional[str] = Field(None, description="AI 评估")
    is_correct: Optional[int] = Field(None, description="是否正确")
    solution: Optional[str] = Field(None, description="解题步骤")
    image_path: Optional[str] = Field(None, description="图片路径")
    difficulty: int = Field(..., description="难度等级")
    wrong_count: int = Field(..., description="错误次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class WrongProblemListResponse(BaseModel):
    """错题列表响应体"""

    items: list[WrongProblemResponse] = Field(..., description="错题列表")
    total: int = Field(..., description="总数")


class AutoCollectRequest(BaseModel):
    """自动收录错题请求体"""

    image_path: str = Field(..., description="图片路径")
    subject: str = Field(..., max_length=50, description="科目")
    knowledge_point: str = Field(..., max_length=200, description="知识点")


class AutoCollectResponse(BaseModel):
    """自动收录错题响应体"""

    wrong_problem: WrongProblemResponse = Field(..., description="收录的错题")
    ocr_text: str = Field(..., description="OCR 识别文本")
    evaluation: str = Field(..., description="AI 评估结果")
    is_correct: bool = Field(..., description="是否回答正确")
