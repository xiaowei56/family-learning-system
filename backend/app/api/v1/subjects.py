"""
科目配置 API 路由

提供科目列表查询和用户科目配置功能。
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.subject import Subject, UserSubject
from app.models.user import User
from app.schemas.subject import (
    SubjectResponse,
    UserSubjectItem,
    UserSubjectsRequest,
    UserSubjectsResponse,
)

# ─── 科目列表路由器（挂载到 /api/v1/subjects）────────
router = APIRouter(tags=["科目配置"])


@router.get(
    "",
    response_model=List[SubjectResponse],
    summary="获取科目列表",
    description="获取系统中所有可用的预设科目列表。",
)
def list_subjects(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[SubjectResponse]:
    """获取所有预设科目。"""
    subjects = db.query(Subject).order_by(Subject.name).all()

    return [
        SubjectResponse(
            id=str(s.id),
            name=s.name,
            created_at=s.created_at,
        )
        for s in subjects
    ]


# ─── 用户科目配置路由器（挂载到 /api/v1/users）───────
user_subjects_router = APIRouter(tags=["用户科目"])


@user_subjects_router.get(
    "/subjects",
    response_model=UserSubjectsResponse,
    summary="获取用户已选科目",
    description="获取当前登录用户已配置的学习科目列表。",
)
def get_user_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSubjectsResponse:
    """获取当前用户的已选科目。"""
    user_subjects = (
        db.query(UserSubject)
        .filter(UserSubject.user_id == current_user.id)
        .all()
    )

    subjects = []
    for us in user_subjects:
        subject = db.query(Subject).filter(Subject.id == us.subject_id).first()
        if subject:
            subjects.append(
                UserSubjectItem(
                    id=str(us.id),
                    subject_id=str(us.subject_id),
                    subject_name=subject.name,
                )
            )

    return UserSubjectsResponse(subjects=subjects)


@user_subjects_router.post(
    "/subjects",
    response_model=UserSubjectsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="设置用户科目",
    description="为当前用户设置学习的科目列表（会覆盖原有配置）。",
    responses={
        201: {"description": "配置成功"},
        404: {"description": "科目不存在"},
    },
)
def set_user_subjects(
    request: UserSubjectsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSubjectsResponse:
    """设置当前用户的科目（覆盖式更新）。"""
    existing_subjects = (
        db.query(Subject).filter(Subject.id.in_(request.subject_ids)).all()
    )
    existing_ids = {str(s.id) for s in existing_subjects}
    requested_ids = set(request.subject_ids)

    invalid_ids = requested_ids - existing_ids
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"科目不存在: {', '.join(invalid_ids)}",
        )

    db.query(UserSubject).filter(
        UserSubject.user_id == current_user.id
    ).delete()

    for subject_id in request.subject_ids:
        user_subject = UserSubject(
            user_id=current_user.id,
            subject_id=subject_id,
        )
        db.add(user_subject)

    db.commit()

    return get_user_subjects(db=db, current_user=current_user)
