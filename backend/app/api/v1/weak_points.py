"""
薄弱点分析与练习试卷 API 路由

提供薄弱点分析、智能出卷和学习诊断报告功能。
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_student_ownership
from app.models.user import User
from app.models.advanced_analysis import LearningAdvice, PracticePaper, WeakPoint
from app.models.wrong_problem import WrongProblem
from app.models.exam_result import ExamResult
from app.schemas.advanced_analysis import (
    LearningAdviceResponse,
    PracticePaperGenerateRequest,
    PracticePaperListResponse,
    PracticePaperResponse,
    WeakPointAnalysisResponse,
    WeakPointResponse,
)
from app.services.llm_service import llm_service

router = APIRouter(tags=["薄弱点分析"])


# ─── 工具函数 ─────────────────────────────────────────

def _weakpoint_to_response(w: WeakPoint) -> WeakPointResponse:
    return WeakPointResponse(
        id=str(w.id),
        student_id=str(w.student_id) if w.student_id else None,
        subject=w.subject,
        knowledge_point=w.knowledge_point,
        mastery_level=w.mastery_level,
        wrong_count=w.wrong_count,
        total_count=w.total_count,
        suggestion=w.suggestion,
        created_at=w.created_at,
    )


def _paper_to_response(p: PracticePaper) -> PracticePaperResponse:
    return PracticePaperResponse(
        id=str(p.id),
        student_id=str(p.student_id) if p.student_id else None,
        subject=p.subject,
        title=p.title,
        questions=p.questions or [],
        target_points=p.target_points or [],
        total_questions=p.total_questions,
        difficulty_distribution=p.difficulty_distribution,
        status=p.status,
        score=p.score,
        created_at=p.created_at,
    )


# ─── 薄弱点分析 ────────────────────────────────────────

@router.get(
    "/weak-points",
    response_model=list[WeakPointResponse],
    summary="获取薄弱点列表",
    description="查询当前用户的薄弱知识点分析结果，按掌握程度升序排列。",
)
def list_weak_points(
    subject: Optional[str] = Query(None, description="科目筛选"),
    student_id: Optional[str] = Query(None, description="所属学生 ID 筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WeakPointResponse]:
    """获取薄弱点列表，按掌握程度从低到高排序。"""
    query = db.query(WeakPoint).filter(WeakPoint.user_id == current_user.id)

    if subject:
        query = query.filter(WeakPoint.subject == subject)

    verify_student_ownership(student_id, current_user, db)
    if student_id:
        query = query.filter(WeakPoint.student_id == student_id)

    items = query.order_by(WeakPoint.mastery_level.asc(), WeakPoint.wrong_count.desc()).all()
    return [_weakpoint_to_response(w) for w in items]


@router.post(
    "/weak-points/analyze",
    response_model=WeakPointAnalysisResponse,
    summary="执行薄弱点分析",
    description="聚合错题和考试成绩数据，调用 LLM 生成综合分析报告。",
)
async def analyze_weak_points(
    student_id: Optional[str] = Query(None, description="所属学生 ID 筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WeakPointAnalysisResponse:
    """聚合错题和考试数据，进行 AI 薄弱点分析。"""
    verify_student_ownership(student_id, current_user, db)

    # 1. 获取错题数据
    wrong_query = db.query(WrongProblem).filter(
        WrongProblem.user_id == current_user.id,
        WrongProblem.is_correct == 0,
    )
    if student_id:
        wrong_query = wrong_query.filter(WrongProblem.student_id == student_id)
    wrong_problems = wrong_query.all()

    # 2. 获取考试成绩
    exam_query = db.query(ExamResult).filter(ExamResult.user_id == current_user.id)
    if student_id:
        exam_query = exam_query.filter(ExamResult.student_id == student_id)
    exam_results = exam_query.order_by(ExamResult.exam_date.desc()).limit(50).all()

    # 3. 构建本地统计（按知识点聚合）
    from collections import defaultdict

    point_stats: dict = defaultdict(lambda: {"wrong": 0, "total": 0})

    for wp in wrong_problems:
        key = f"{wp.subject}::{wp.knowledge_point}"
        point_stats[key]["wrong"] += 1
        point_stats[key]["total"] += 1
        point_stats[key]["subject"] = wp.subject
        point_stats[key]["point"] = wp.knowledge_point

    # 计算掌握程度
    weak_points_data = []
    for key, stats in point_stats.items():
        mastery = 1.0 - (stats["wrong"] / max(stats["total"], 1))
        weak_points_data.append({
            "subject": stats["subject"],
            "knowledge_point": stats["point"],
            "mastery_level": round(mastery, 2),
            "wrong_count": stats["wrong"],
            "total_count": stats["total"],
        })

    # 4. 调用 LLM 进行智能分析
    wp_list = [
        {"subject": d["subject"], "knowledge_point": d["knowledge_point"],
         "wrong_count": d["wrong_count"]}
        for d in weak_points_data
    ]
    exam_list = [
        {"subject": r.subject, "exam_type": r.exam_type,
         "score_rate": r.score_rate, "exam_date": str(r.exam_date)}
        for r in exam_results
    ]

    llm_result = await llm_service.analyze_weak_points(wp_list, exam_list)

    # 5. 保存分析结果
    # 清除旧记录
    db.query(WeakPoint).filter(WeakPoint.user_id == current_user.id).delete()

    for d in weak_points_data:
        suggestion = ""
        if llm_result and llm_result.get("weak_points"):
            for wp in llm_result["weak_points"]:
                if wp.get("knowledge_point") == d["knowledge_point"]:
                    suggestion = wp.get("suggestion", "")
                    break

        wp = WeakPoint(
            user_id=current_user.id,
            subject=d["subject"],
            knowledge_point=d["knowledge_point"],
            mastery_level=d["mastery_level"],
            wrong_count=d["wrong_count"],
            total_count=d["total_count"],
            suggestion=suggestion,
        )
        db.add(wp)

    # 6. 保存学习建议
    advice = LearningAdvice(
        user_id=current_user.id,
        overall_diagnosis=llm_result.get("overall_diagnosis", "") if llm_result else "",
        study_plan=llm_result.get("study_plan", "") if llm_result else "",
        weak_points_detail=weak_points_data,
        suggestions=[wp.get("suggestion", "") for wp in
                     (llm_result.get("weak_points", []) if llm_result else [])],
    )
    db.add(advice)
    db.commit()

    # 返回结果
    saved_points = (
        db.query(WeakPoint)
        .filter(WeakPoint.user_id == current_user.id)
        .order_by(WeakPoint.mastery_level.asc())
        .all()
    )

    return WeakPointAnalysisResponse(
        weak_points=[_weakpoint_to_response(w) for w in saved_points],
        overall_diagnosis=llm_result.get("overall_diagnosis", "分析完成") if llm_result else "分析完成",
        study_plan=llm_result.get("study_plan", "") if llm_result else "",
    )


# ─── 练习试卷 ─────────────────────────────────────────

@router.get(
    "/practice-papers",
    response_model=PracticePaperListResponse,
    summary="获取练习试卷列表",
)
def list_practice_papers(
    subject: Optional[str] = Query(None, description="科目筛选"),
    student_id: Optional[str] = Query(None, description="所属学生 ID 筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PracticePaperListResponse:
    """获取当前用户的练习试卷列表。"""
    query = db.query(PracticePaper).filter(PracticePaper.user_id == current_user.id)

    if subject:
        query = query.filter(PracticePaper.subject == subject)

    verify_student_ownership(student_id, current_user, db)
    if student_id:
        query = query.filter(PracticePaper.student_id == student_id)

    total = query.count()
    items = (
        query.order_by(PracticePaper.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PracticePaperListResponse(
        items=[_paper_to_response(p) for p in items],
        total=total,
    )


@router.get(
    "/practice-papers/{paper_id}",
    response_model=PracticePaperResponse,
    summary="获取练习试卷详情",
)
def get_practice_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PracticePaperResponse:
    """获取指定练习试卷的详细信息。"""
    paper = (
        db.query(PracticePaper)
        .filter(PracticePaper.id == paper_id, PracticePaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="练习试卷不存在")
    return _paper_to_response(paper)


@router.post(
    "/practice-papers/generate",
    response_model=PracticePaperResponse,
    status_code=201,
    summary="生成练习试卷",
    description="基于薄弱知识点调用 LLM 生成针对性练习试卷。",
)
async def generate_practice_paper(
    data: PracticePaperGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PracticePaperResponse:
    """基于薄弱知识点，调用 LLM 生成练习试卷。"""
    verify_student_ownership(data.student_id, current_user, db)

    # 获取薄弱点数据
    weak_points = (
        db.query(WeakPoint)
        .filter(
            WeakPoint.user_id == current_user.id,
            WeakPoint.subject == data.subject,
            WeakPoint.knowledge_point.in_(data.weak_points),
        )
        .all()
    )

    wp_list = [
        {"subject": w.subject, "knowledge_point": w.knowledge_point,
         "mastery_level": w.mastery_level}
        for w in weak_points
    ]

    # 如果没有已有的薄弱点，构造基本数据
    if not wp_list:
        wp_list = [{"subject": data.subject, "knowledge_point": p,
                     "mastery_level": 0.5} for p in data.weak_points]

    # 调用 LLM 生成
    questions = await llm_service.generate_practice_paper(
        weak_points=wp_list,
        subject=data.subject,
        question_count=data.question_count,
    )

    if not questions:
        raise HTTPException(status_code=503, detail="试卷生成服务暂不可用")

    # 统计难度分布
    diff_dist = {"simple": 0, "medium": 0, "hard": 0}
    for q in questions:
        d = q.get("difficulty", 1)
        if d == 1:
            diff_dist["simple"] += 1
        elif d == 2:
            diff_dist["medium"] += 1
        else:
            diff_dist["hard"] += 1

    # 创建试卷记录
    paper = PracticePaper(
        user_id=current_user.id,
        student_id=data.student_id,
        subject=data.subject,
        title=f"{data.subject}薄弱点专项练习 ({len(questions)}题)",
        questions=questions,
        target_points=data.weak_points,
        total_questions=len(questions),
        difficulty_distribution=diff_dist,
        status="generated",
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    return _paper_to_response(paper)


@router.put(
    "/practice-papers/{paper_id}/status",
    response_model=PracticePaperResponse,
    summary="更新练习状态",
)
def update_practice_status(
    paper_id: str,
    status: str = Query(..., pattern=r"^(started|completed)$"),
    score: Optional[float] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PracticePaperResponse:
    """更新练习试卷状态（开始/完成）和得分。"""
    paper = (
        db.query(PracticePaper)
        .filter(PracticePaper.id == paper_id, PracticePaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="练习试卷不存在")

    paper.status = status
    if score is not None:
        paper.score = score
    db.commit()
    db.refresh(paper)
    return _paper_to_response(paper)


@router.delete(
    "/practice-papers/{paper_id}",
    status_code=204,
    summary="删除练习试卷",
)
def delete_practice_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除指定练习试卷。"""
    paper = (
        db.query(PracticePaper)
        .filter(PracticePaper.id == paper_id, PracticePaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="练习试卷不存在")
    db.delete(paper)
    db.commit()


# ─── 学习诊断报告 ─────────────────────────────────────

@router.get(
    "/learning-advice",
    response_model=LearningAdviceResponse,
    summary="获取最新学习建议",
    description="获取最近一次生成的综合性学习诊断报告。",
)
def get_latest_advice(
    student_id: Optional[str] = Query(None, description="所属学生 ID 筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LearningAdviceResponse:
    """获取最新的学习诊断报告。"""
    verify_student_ownership(student_id, current_user, db)

    query = db.query(LearningAdvice).filter(LearningAdvice.user_id == current_user.id)
    if student_id:
        query = query.filter(LearningAdvice.student_id == student_id)
    advice = query.order_by(LearningAdvice.created_at.desc()).first()
    if not advice:
        raise HTTPException(status_code=404, detail="暂无学习诊断报告，请先执行薄弱点分析")

    return LearningAdviceResponse(
        id=str(advice.id),
        subject=advice.subject,
        overall_diagnosis=advice.overall_diagnosis,
        study_plan=advice.study_plan,
        weak_points_detail=advice.weak_points_detail or [],
        suggestions=advice.suggestions or [],
        created_at=advice.created_at,
    )
