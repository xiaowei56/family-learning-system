"""
学习记录与复习计划 API 路由

提供学习记录的 CRUD 操作和基于艾宾浩斯遗忘曲线的复习管理。
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.study_record import ReviewSchedule, StudyRecord
from app.models.user import User
from app.schemas.study_record import (
    DailyReviewResponse,
    ReviewRecordItem,
    SpeedUpdateRequest,
    StudyRecordCreate,
    StudyRecordResponse,
    StudyRecordUpdate,
    SubjectReviewGroup,
)
from app.services.memory_curve import calculate_review_dates

router = APIRouter(prefix="/study-records", tags=["学习记录"])
reviews_router = APIRouter(prefix="/reviews", tags=["复习管理"])


# ═══════════════════════════════════════════════════════
# 学习记录 CRUD
# ═══════════════════════════════════════════════════════


@router.get(
    "",
    response_model=list[StudyRecordResponse],
    summary="获取学习记录列表",
    description="获取当前用户的学习记录列表，可按科目筛选，按创建时间倒序排列。",
)
def list_study_records(
    subject: str | None = Query(None, description="科目名称筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[StudyRecordResponse]:
    """获取当前用户的学习记录列表。"""
    query = db.query(StudyRecord).filter(StudyRecord.user_id == current_user.id)
    if subject:
        query = query.filter(StudyRecord.subject == subject)
    records = query.order_by(StudyRecord.created_at.desc()).all()
    return [_record_to_response(r) for r in records]


@router.post(
    "",
    response_model=StudyRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建学习记录",
    description="创建新的学习记录，并自动生成基于艾宾浩斯遗忘曲线的复习排期。",
)
def create_study_record(
    request: StudyRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudyRecordResponse:
    """创建学习记录并自动生成复习排期。"""
    record = StudyRecord(
        user_id=current_user.id,
        subject=request.subject,
        title=request.title,
        content=request.content,
        tags=request.tags,
    )
    db.add(record)
    db.flush()  # 获取 record.id

    # ─── 自动生成复习排期 ──────────────────────────
    created_date = record.created_at.date()
    review_dates = calculate_review_dates(created_date, speed_mode="medium")
    for i, review_date in enumerate(review_dates):
        schedule = ReviewSchedule(
            study_record_id=record.id,
            review_date=review_date,
            review_count=i + 1,
            status="pending",
            speed_mode="medium",
        )
        db.add(schedule)

    db.commit()
    db.refresh(record)
    return _record_to_response(record)


@router.get(
    "/{record_id}",
    response_model=StudyRecordResponse,
    summary="获取学习记录详情",
    description="根据 ID 获取单条学习记录的详细信息。",
)
def get_study_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudyRecordResponse:
    """获取单条学习记录。"""
    record = _get_user_record_or_404(db, current_user.id, record_id)
    return _record_to_response(record)


@router.put(
    "/{record_id}",
    response_model=StudyRecordResponse,
    summary="更新学习记录",
    description="更新指定学习记录的字段内容，只传需要修改的字段即可。",
)
def update_study_record(
    record_id: UUID,
    request: StudyRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudyRecordResponse:
    """更新学习记录（部分更新）。"""
    record = _get_user_record_or_404(db, current_user.id, record_id)

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return _record_to_response(record)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除学习记录",
    description="删除指定的学习记录及其关联的复习计划（级联删除）。",
)
def delete_study_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除学习记录及关联的复习排期。"""
    record = _get_user_record_or_404(db, current_user.id, record_id)
    db.delete(record)
    db.commit()


# ═══════════════════════════════════════════════════════
# 复习管理
# ═══════════════════════════════════════════════════════


@reviews_router.get(
    "/today",
    response_model=DailyReviewResponse,
    summary="获取今日复习列表",
    description="获取当前用户今日到期的复习安排，按科目分组返回。",
)
def get_today_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DailyReviewResponse:
    """获取今日到期的复习安排，按科目分组。"""
    today = date.today()

    schedules = (
        db.query(ReviewSchedule)
        .join(StudyRecord)
        .filter(
            ReviewSchedule.status == "pending",
            ReviewSchedule.review_date <= today,
            StudyRecord.user_id == current_user.id,
        )
        .order_by(StudyRecord.subject, ReviewSchedule.review_date.asc())
        .all()
    )

    # 按科目分组
    subject_groups: dict[str, list[ReviewRecordItem]] = {}
    for s in schedules:
        subject = s.study_record.subject
        if subject not in subject_groups:
            subject_groups[subject] = []
        subject_groups[subject].append(
            ReviewRecordItem(
                id=str(s.id),
                study_record_id=str(s.study_record_id),
                title=s.study_record.title,
                subject=subject,
                review_count=s.review_count,
                status=s.status,
                speed_mode=s.speed_mode,
            )
        )

    groups = [
        SubjectReviewGroup(subject=subj, records=recs, count=len(recs))
        for subj, recs in subject_groups.items()
    ]

    total = sum(g.count for g in groups)

    return DailyReviewResponse(subjects=groups, total=total)


@reviews_router.put(
    "/{review_id}/master",
    summary="标记为已掌握",
    description="将复习安排标记为已掌握状态，并自动取消该学习记录的所有未来待复习计划。",
)
def mark_as_mastered(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """标记复习为已掌握，取消该学习记录的所有未来复习。"""
    schedule = _get_user_review_or_404(db, current_user.id, review_id)

    schedule.status = "mastered"
    db.commit()

    # 取消该学习记录的其他所有 pending 复习
    db.query(ReviewSchedule).filter(
        ReviewSchedule.study_record_id == schedule.study_record_id,
        ReviewSchedule.id != schedule.id,
        ReviewSchedule.status == "pending",
    ).update({"status": "mastered"})
    db.commit()

    return {"message": "已标记为已掌握", "id": str(review_id)}


@reviews_router.put(
    "/{review_id}/speed",
    summary="调整复习速度",
    description="修改复习速度模式（fast/medium/slow），自动重新计算未来的复习日期。",
)
def update_review_speed(
    review_id: UUID,
    request: SpeedUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """调整复习速度模式并重新生成未来复习排期。"""
    schedule = _get_user_review_or_404(db, current_user.id, review_id)

    if schedule.speed_mode == request.speed_mode:
        return {
            "message": "速度模式未变化",
            "id": str(review_id),
            "speed_mode": request.speed_mode,
        }

    # 删除该学习记录所有未来的 pending 复习（不包括当前这条）
    db.query(ReviewSchedule).filter(
        ReviewSchedule.study_record_id == schedule.study_record_id,
        ReviewSchedule.id != schedule.id,
        ReviewSchedule.status == "pending",
    ).delete()
    db.commit()

    # 根据新速度模式重算复习日期，追加当前复习计数之后的条目
    created_date = schedule.study_record.created_at.date()
    new_dates = calculate_review_dates(created_date, speed_mode=request.speed_mode)

    for i, review_date in enumerate(new_dates):
        count = i + 1
        if count <= schedule.review_count:
            continue
        new_schedule = ReviewSchedule(
            study_record_id=schedule.study_record_id,
            review_date=review_date,
            review_count=count,
            status="pending",
            speed_mode=request.speed_mode,
        )
        db.add(new_schedule)

    schedule.speed_mode = request.speed_mode
    db.commit()

    return {
        "message": "速度模式已更新",
        "id": str(review_id),
        "speed_mode": request.speed_mode,
    }


# ═══════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════


def _get_user_record_or_404(
    db: Session, user_id: UUID, record_id: UUID
) -> StudyRecord:
    """获取属于当前用户的学习记录，不存在则抛出 404。"""
    record = (
        db.query(StudyRecord)
        .filter(StudyRecord.id == record_id, StudyRecord.user_id == user_id)
        .first()
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习记录不存在",
        )
    return record


def _get_user_review_or_404(
    db: Session, user_id: UUID, review_id: UUID
) -> ReviewSchedule:
    """获取属于当前用户的复习安排，不存在则抛出 404。"""
    schedule = (
        db.query(ReviewSchedule)
        .join(StudyRecord)
        .filter(
            ReviewSchedule.id == review_id,
            StudyRecord.user_id == user_id,
        )
        .first()
    )
    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="复习记录不存在",
        )
    return schedule


def _record_to_response(record: StudyRecord) -> StudyRecordResponse:
    """将 ORM StudyRecord 转换为响应体。"""
    return StudyRecordResponse(
        id=str(record.id),
        subject=record.subject,
        title=record.title,
        content=record.content,
        tags=record.tags or [],
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
