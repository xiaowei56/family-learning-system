"""
仪表盘 API 路由

提供首页仪表盘摘要数据聚合接口，整合今日复习、近期错题、考试成绩等模块信息。
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_student_ownership
from app.models.exam_result import ExamResult
from app.models.study_record import ReviewSchedule, StudyRecord
from app.models.user import User
from app.schemas.dashboard import (
    DashboardResponse,
    LatestScoreItem,
    RecentWrong,
    RecentWrongItem,
    ScoreSummary,
    TodayReviews,
)

router = APIRouter(tags=["仪表盘"])


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="获取仪表盘摘要",
    description=(
        "返回当前用户的首页仪表盘数据，包括："
        "今日待复习统计（按科目分组）、近期错题（最近 5 条）、各科目最新得分率。"
    ),
)
def get_dashboard(
    student_id: Optional[str] = Query(None, description="所属学生 ID 筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardResponse:
    """获取当前用户的仪表盘摘要数据。"""
    verify_student_ownership(student_id, current_user, db)

    # ─── 今日复习 ────────────────────────────────────
    today = date.today()
    pending_schedules = (
        db.query(ReviewSchedule)
        .join(StudyRecord)
        .filter(
            ReviewSchedule.status == "pending",
            ReviewSchedule.review_date <= today,
            StudyRecord.user_id == current_user.id,
        )
        .all()
    )

    if student_id:
        pending_schedules = [s for s in pending_schedules if str(s.student_id) == student_id]

    # 按科目去重统计
    subject_set: set[str] = set()
    for s in pending_schedules:
        subject_set.add(s.study_record.subject)

    today_reviews = TodayReviews(
        total=len(pending_schedules),
        subjects=sorted(subject_set),
    )

    # ─── 近期错题 ────────────────────────────────────
    recent_wrong = RecentWrong(total=0, items=[])

    # ─── 得分率摘要 ──────────────────────────────────
    base_filter = [ExamResult.user_id == current_user.id]
    if student_id:
        base_filter.append(ExamResult.student_id == student_id)

    subjects_q = (
        db.query(ExamResult.subject)
        .filter(*base_filter)
        .distinct()
        .order_by(ExamResult.subject)
        .all()
    )
    subject_list = [s[0] for s in subjects_q]

    latest_items: list[LatestScoreItem] = []
    for subject_name in subject_list:
        latest = (
            db.query(ExamResult)
            .filter(
                ExamResult.user_id == current_user.id,
                ExamResult.subject == subject_name,
                *(ExamResult.student_id == student_id if student_id else [])
            )
            .order_by(ExamResult.exam_date.desc())
            .first()
        )
        if latest:
            latest_items.append(
                LatestScoreItem(
                    subject=latest.subject,
                    score_rate=latest.score_rate,
                )
            )

    score_summary = ScoreSummary(
        subjects=subject_list,
        latest=latest_items,
    )

    return DashboardResponse(
        today_reviews=today_reviews,
        recent_wrong=recent_wrong,
        score_summary=score_summary,
    )
