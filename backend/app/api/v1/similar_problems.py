"""
举一反三 API 路由

提供相似题目生成、查询和管理功能。
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.advanced_analysis import SimilarProblem
from app.schemas.advanced_analysis import (
    SimilarProblemGenerateRequest,
    SimilarProblemGenerateResponse,
    SimilarProblemListResponse,
    SimilarProblemResponse,
)
from app.services.llm_service import llm_service

router = APIRouter(tags=["举一反三"])


def _to_response(p: SimilarProblem) -> SimilarProblemResponse:
    return SimilarProblemResponse(
        id=str(p.id),
        subject=p.subject,
        knowledge_point=p.knowledge_point,
        problem_text=p.problem_text,
        answer=p.answer,
        solution=p.solution,
        difficulty=p.difficulty,
        is_practiced=p.is_practiced,
        created_at=p.created_at,
    )


@router.get(
    "/similar-problems",
    response_model=SimilarProblemListResponse,
    summary="获取相似题列表",
    description="查询所有已生成的相似题目，支持科目、知识点筛选。",
)
def list_similar_problems(
    subject: Optional[str] = Query(None, description="科目筛选"),
    knowledge_point: Optional[str] = Query(None, description="知识点筛选"),
    is_practiced: Optional[int] = Query(None, description="练习状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SimilarProblemListResponse:
    """获取当前用户的相似题目列表。"""
    query = db.query(SimilarProblem).filter(SimilarProblem.user_id == current_user.id)

    if subject:
        query = query.filter(SimilarProblem.subject == subject)
    if knowledge_point:
        query = query.filter(SimilarProblem.knowledge_point.ilike(f"%{knowledge_point}%"))
    if is_practiced is not None:
        query = query.filter(SimilarProblem.is_practiced == is_practiced)

    total = query.count()
    items = (
        query.order_by(SimilarProblem.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return SimilarProblemListResponse(
        items=[_to_response(p) for p in items],
        total=total,
    )


@router.get(
    "/similar-problems/{problem_id}",
    response_model=SimilarProblemResponse,
    summary="获取相似题详情",
)
def get_similar_problem(
    problem_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SimilarProblemResponse:
    """获取单条相似题目的详细信息。"""
    problem = (
        db.query(SimilarProblem)
        .filter(SimilarProblem.id == problem_id, SimilarProblem.user_id == current_user.id)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="相似题目不存在")
    return _to_response(problem)


@router.post(
    "/similar-problems/generate",
    response_model=SimilarProblemGenerateResponse,
    summary="生成相似题",
    description="调用 LLM 根据原题生成一道相似练习题。",
)
async def generate_similar_problem(
    data: SimilarProblemGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SimilarProblemGenerateResponse:
    """调用 LLM 生成一道相似练习题，并保存到数据库。"""
    result = await llm_service.generate_similar_problem(
        problem_text=data.problem_text,
        subject=data.subject,
        knowledge_point=data.knowledge_point,
    )
    if not result:
        raise HTTPException(status_code=503, detail="相似题生成服务暂不可用")

    # 保存到数据库
    problem = SimilarProblem(
        user_id=current_user.id,
        source_problem_id=uuid.UUID(data.source_problem_id) if data.source_problem_id else None,
        subject=data.subject,
        knowledge_point=data.knowledge_point,
        problem_text=result.get("problem", ""),
        answer=result.get("answer", ""),
        solution=result.get("solution", ""),
        difficulty=result.get("difficulty", 1),
    )
    db.add(problem)
    db.commit()

    return SimilarProblemGenerateResponse(
        problem=problem.problem_text,
        answer=problem.answer or "",
        solution=problem.solution or "",
        difficulty=problem.difficulty,
    )


@router.put(
    "/similar-problems/{problem_id}/practice",
    response_model=SimilarProblemResponse,
    summary="标记已练习",
)
def mark_practiced(
    problem_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SimilarProblemResponse:
    """标记相似题目为已练习。"""
    problem = (
        db.query(SimilarProblem)
        .filter(SimilarProblem.id == problem_id, SimilarProblem.user_id == current_user.id)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="相似题目不存在")

    problem.is_practiced = 1
    db.commit()
    db.refresh(problem)
    return _to_response(problem)


@router.delete(
    "/similar-problems/{problem_id}",
    status_code=204,
    summary="删除相似题",
)
def delete_similar_problem(
    problem_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除指定相似题。"""
    problem = (
        db.query(SimilarProblem)
        .filter(SimilarProblem.id == problem_id, SimilarProblem.user_id == current_user.id)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="相似题目不存在")
    db.delete(problem)
    db.commit()
