"""
考试成绩 API 路由

提供考试成绩的增删改查、趋势分析和摘要统计功能，所有接口需要 JWT 认证。
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.exam_result import ExamResult
from app.models.user import User
from app.schemas.exam_result import (
    ExamResultCreate,
    ExamResultResponse,
    ExamResultUpdate,
    LatestResult,
    SummaryResponse,
    TrendDataPoint,
    TrendResponse,
    TrendSeries,
)

router = APIRouter(tags=["考试成绩"])


# ─── 工具函数 ────────────────────────────────────────

def _exam_result_to_response(r: ExamResult) -> ExamResultResponse:
    """将 ORM 模型转换为响应体。"""
    return ExamResultResponse(
        id=str(r.id),
        user_id=str(r.user_id),
        subject=r.subject,
        exam_type=r.exam_type.value if hasattr(r.exam_type, "value") else r.exam_type,
        score=r.score,
        total_score=r.total_score,
        score_rate=r.score_rate,
        exam_date=r.exam_date,
        notes=r.notes,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


def _compute_score_rate(score: float, total_score: float) -> float:
    """计算得分率。"""
    return round(score / total_score, 4)


# ─── 列表查询 ────────────────────────────────────────

@router.get(
    "/exam-results",
    response_model=list[ExamResultResponse],
    summary="获取考试成绩列表",
    description="获取当前用户的所有考试成绩，支持按科目和考试类型筛选。",
)
def list_exam_results(
    subject: Optional[str] = Query(None, description="科目名称筛选"),
    exam_type: Optional[str] = Query(None, description="考试类型筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ExamResultResponse]:
    """获取当前用户的考试成绩列表。"""
    query = (
        db.query(ExamResult)
        .filter(ExamResult.user_id == current_user.id)
    )

    if subject:
        query = query.filter(ExamResult.subject == subject)
    if exam_type:
        query = query.filter(ExamResult.exam_type == exam_type)

    results = query.order_by(ExamResult.exam_date.desc()).all()

    return [_exam_result_to_response(r) for r in results]


# ─── 创建 ────────────────────────────────────────────

@router.post(
    "/exam-results",
    response_model=ExamResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建考试成绩",
    description="记录新的考试成绩，得分率自动计算。",
    responses={
        201: {"description": "创建成功"},
        422: {"description": "数据校验失败（如得分超过满分）"},
    },
)
def create_exam_result(
    request: ExamResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExamResultResponse:
    """记录新的考试成绩。"""
    result = ExamResult(
        user_id=current_user.id,
        subject=request.subject,
        exam_type=request.exam_type,
        score=request.score,
        total_score=request.total_score,
        score_rate=_compute_score_rate(request.score, request.total_score),
        exam_date=request.exam_date,
        notes=request.notes,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return _exam_result_to_response(result)


# ─── 趋势图数据 ─────────────────────────────────────

@router.get(
    "/exam-results/trend",
    response_model=TrendResponse,
    summary="获取得分率趋势图数据",
    description="按科目分组返回得分率趋势数据，支持多科目对比和考试类型筛选。",
)
def get_exam_trend(
    subjects: str = Query(
        ...,
        description="科目名称列表，用逗号分隔，如：数学,物理",
    ),
    exam_type: Optional[str] = Query(
        None,
        description="考试类型筛选（可选）",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrendResponse:
    """获取得分率趋势图数据。"""
    subject_list = [s.strip() for s in subjects.split(",") if s.strip()]

    series_list: list[TrendSeries] = []
    for subject in subject_list:
        query = (
            db.query(ExamResult)
            .filter(
                ExamResult.user_id == current_user.id,
                ExamResult.subject == subject,
            )
        )
        if exam_type:
            query = query.filter(ExamResult.exam_type == exam_type)

        records = query.order_by(ExamResult.exam_date.asc()).all()

        if not records:
            continue

        data_points = [
            TrendDataPoint(
                date=r.exam_date,
                score_rate=r.score_rate,
                score=r.score,
                total_score=r.total_score,
                exam_type=r.exam_type.value
                if hasattr(r.exam_type, "value")
                else r.exam_type,
            )
            for r in records
        ]
        series_list.append(TrendSeries(subject=subject, data=data_points))

    return TrendResponse(series=series_list)


# ─── 摘要统计 ───────────────────────────────────────

@router.get(
    "/exam-results/summary",
    response_model=SummaryResponse,
    summary="获取考试成绩摘要",
    description="返回当前用户的科目列表、考试类型列表及各科目最新成绩。",
)
def get_exam_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SummaryResponse:
    """获取考试成绩摘要统计。"""
    # 获取所有去重科目
    subjects_q = (
        db.query(ExamResult.subject)
        .filter(ExamResult.user_id == current_user.id)
        .distinct()
        .order_by(ExamResult.subject)
        .all()
    )
    subject_list = [s[0] for s in subjects_q]

    # 获取所有去重考试类型
    exam_types_q = (
        db.query(ExamResult.exam_type)
        .filter(ExamResult.user_id == current_user.id)
        .distinct()
        .order_by(ExamResult.exam_type)
        .all()
    )
    exam_type_list = [
        t[0].value if hasattr(t[0], "value") else t[0] for t in exam_types_q
    ]

    # 获取各科目最新考试成绩（使用子查询）
    latest_records: list[ExamResult] = []
    for subject in subject_list:
        latest = (
            db.query(ExamResult)
            .filter(
                ExamResult.user_id == current_user.id,
                ExamResult.subject == subject,
            )
            .order_by(ExamResult.exam_date.desc())
            .first()
        )
        if latest:
            latest_records.append(latest)

    latest_results = [
        LatestResult(
            subject=r.subject,
            score_rate=r.score_rate,
            exam_date=r.exam_date,
        )
        for r in latest_records
    ]

    return SummaryResponse(
        subjects=subject_list,
        exam_types=exam_type_list,
        latest=latest_results,
    )


# ─── 获取单条 ───────────────────────────────────────

@router.get(
    "/exam-results/{result_id}",
    response_model=ExamResultResponse,
    summary="获取考试成绩详情",
    description="根据 ID 获取单条考试成绩的详细信息。",
    responses={
        200: {"description": "查询成功"},
        404: {"description": "考试成绩不存在"},
        403: {"description": "无权访问该记录"},
    },
)
def get_exam_result(
    result_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExamResultResponse:
    """获取单条考试成绩详情。"""
    result = db.query(ExamResult).filter(ExamResult.id == result_id).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试成绩不存在",
        )

    if result.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该记录",
        )

    return _exam_result_to_response(result)


# ─── 更新 ────────────────────────────────────────────

@router.put(
    "/exam-results/{result_id}",
    response_model=ExamResultResponse,
    summary="更新考试成绩",
    description="更新指定的考试成绩信息，若修改了分数则自动重算得分率。",
    responses={
        200: {"description": "更新成功"},
        404: {"description": "考试成绩不存在"},
        403: {"description": "无权操作该记录"},
        422: {"description": "数据校验失败（如得分超过满分）"},
    },
)
def update_exam_result(
    result_id: UUID,
    request: ExamResultUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExamResultResponse:
    """更新考试成绩。"""
    result = db.query(ExamResult).filter(ExamResult.id == result_id).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试成绩不存在",
        )

    if result.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该记录",
        )

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(result, field, value)

    # 若修改了分数或满分，自动重算得分率
    if "score" in update_data or "total_score" in update_data:
        score = update_data.get("score", result.score)
        # 重新获取 total_score，可能已在 update_data 中
        total_score_value = update_data.get("total_score", result.total_score)
        # 校验：得分不能超过满分
        if score > total_score_value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="得分不能超过满分",
            )
        result.score_rate = _compute_score_rate(score, total_score_value)

    db.commit()
    db.refresh(result)

    return _exam_result_to_response(result)


# ─── 删除 ────────────────────────────────────────────

@router.delete(
    "/exam-results/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除考试成绩",
    description="删除指定的考试成绩记录。",
    responses={
        204: {"description": "删除成功"},
        404: {"description": "考试成绩不存在"},
        403: {"description": "无权操作该记录"},
    },
)
def delete_exam_result(
    result_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除考试成绩。"""
    result = db.query(ExamResult).filter(ExamResult.id == result_id).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试成绩不存在",
        )

    if result.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该记录",
        )

    db.delete(result)
    db.commit()
