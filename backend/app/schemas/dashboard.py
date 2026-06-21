"""
仪表盘 Pydantic 模式

定义首页仪表盘摘要数据的响应体数据结构。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TodayReviews(BaseModel):
    """今日复习汇总"""

    total: int = Field(..., description="待复习总数")
    subjects: list[str] = Field(..., description="涉及科目列表")


class RecentWrongItem(BaseModel):
    """近期错题条目"""

    subject: str = Field(..., description="科目名称")
    knowledge_point: str = Field(..., description="知识点")
    created_at: datetime = Field(..., description="记录时间")


class RecentWrong(BaseModel):
    """近期错题汇总"""

    total: int = Field(..., description="错题总数")
    items: list[RecentWrongItem] = Field(..., description="错题列表")


class LatestScoreItem(BaseModel):
    """最新考试成绩条目"""

    subject: str = Field(..., description="科目名称")
    score_rate: float = Field(..., description="得分率")


class ScoreSummary(BaseModel):
    """得分率摘要"""

    subjects: list[str] = Field(..., description="科目列表")
    latest: list[LatestScoreItem] = Field(..., description="各科目最新成绩")


class DashboardResponse(BaseModel):
    """仪表盘摘要响应体"""

    today_reviews: TodayReviews = Field(..., description="今日复习摘要")
    recent_wrong: RecentWrong = Field(..., description="近期错题摘要")
    score_summary: ScoreSummary = Field(..., description="得分率摘要")
