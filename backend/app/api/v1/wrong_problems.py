"""
错题管理 API 路由

提供 OCR 识别、AI 评估、解题生成、错题 CRUD 及自动收录功能。
涉及 Phase 2 核心——试卷 OCR 识别与错题整理闭环。
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_student_ownership
from app.models.user import User
from app.models.wrong_problem import WrongProblem
from app.schemas.wrong_problem import (
    AIEvaluationRequest,
    AIEvaluationResponse,
    AutoCollectRequest,
    AutoCollectResponse,
    OCRRequest,
    OCRResponse,
    SolutionRequest,
    SolutionResponse,
    WrongProblemCreate,
    WrongProblemListResponse,
    WrongProblemResponse,
    WrongProblemUpdate,
)
from app.services.llm_service import llm_service
from app.services.minio_client import MinioService

router = APIRouter(tags=["错题管理"])


def _problem_to_response(p: WrongProblem) -> WrongProblemResponse:
    """将 ORM 模型转换为响应体。"""
    return WrongProblemResponse(
        id=str(p.id),
        user_id=str(p.user_id),
        subject=p.subject,
        knowledge_point=p.knowledge_point,
        problem_text=p.problem_text,
        student_answer=p.student_answer,
        correct_answer=p.correct_answer,
        ai_evaluation=p.ai_evaluation,
        is_correct=p.is_correct,
        solution=p.solution,
        image_path=p.image_path,
        difficulty=p.difficulty,
        student_id=str(p.student_id) if p.student_id else None,
        wrong_count=p.wrong_count,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


# ─── 图片上传 ─────────────────────────────────────────

@router.post(
    "/wrong-problems/upload",
    summary="上传图片",
    description="上传试卷/题目图片到 MinIO 存储，返回图片路径。",
)
async def upload_image(
    file: UploadFile = File(..., description="图片文件（jpg/png）"),
    current_user: User = Depends(get_current_user),
) -> dict:
    """上传图片并返回 MinIO 路径。"""
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="仅支持 JPEG 和 PNG 格式")

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 20MB")

    filename = f"papers/{current_user.id}/{uuid.uuid4().hex}_{file.filename}"
    minio_service = MinioService()
    url = minio_service.upload_file(content, filename, content_type=file.content_type)

    return {"image_path": filename, "url": url}


# ─── 错题 CRUD ────────────────────────────────────────

@router.get(
    "/wrong-problems",
    response_model=WrongProblemListResponse,
    summary="获取错题列表",
    description="按科目、知识点、难度等条件查询错题列表，支持分页。",
)
def list_wrong_problems(
    subject: Optional[str] = Query(None, description="科目筛选"),
    knowledge_point: Optional[str] = Query(None, description="知识点筛选"),
    difficulty: Optional[int] = Query(None, ge=1, le=3, description="难度筛选"),
    is_correct: Optional[int] = Query(None, description="是否正确：0=错误，1=正确"),
    student_id: Optional[str] = Query(None, description="所属学生 ID 筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WrongProblemListResponse:
    """获取当前用户的错题列表。"""
    verify_student_ownership(student_id, current_user, db)
    query = db.query(WrongProblem).filter(WrongProblem.user_id == current_user.id)

    if subject:
        query = query.filter(WrongProblem.subject == subject)
    if knowledge_point:
        query = query.filter(WrongProblem.knowledge_point.ilike(f"%{knowledge_point}%"))
    if difficulty is not None:
        query = query.filter(WrongProblem.difficulty == difficulty)
    if is_correct is not None:
        query = query.filter(WrongProblem.is_correct == is_correct)
    if student_id:
        query = query.filter(WrongProblem.student_id == student_id)

    total = query.count()
    items = (
        query.order_by(WrongProblem.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return WrongProblemListResponse(
        items=[_problem_to_response(p) for p in items],
        total=total,
    )


@router.get(
    "/wrong-problems/{problem_id}",
    response_model=WrongProblemResponse,
    summary="获取错题详情",
)
def get_wrong_problem(
    problem_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WrongProblemResponse:
    """获取单条错题的详细信息。"""
    problem = (
        db.query(WrongProblem)
        .filter(WrongProblem.id == problem_id, WrongProblem.user_id == current_user.id)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="错题不存在")
    return _problem_to_response(problem)


@router.post(
    "/wrong-problems",
    response_model=WrongProblemResponse,
    status_code=201,
    summary="手动录入错题",
)
def create_wrong_problem(
    data: WrongProblemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WrongProblemResponse:
    """手动录入一条错题记录。"""
    verify_student_ownership(data.student_id, current_user, db)
    problem = WrongProblem(
        user_id=current_user.id,
        student_id=data.student_id,
        subject=data.subject,
        knowledge_point=data.knowledge_point,
        problem_text=data.problem_text,
        student_answer=data.student_answer,
        correct_answer=data.correct_answer,
        ai_evaluation=data.ai_evaluation,
        is_correct=data.is_correct,
        solution=data.solution,
        image_path=data.image_path,
        difficulty=data.difficulty or 1,
        wrong_count=0 if data.is_correct == 1 else 1,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return _problem_to_response(problem)


@router.put(
    "/wrong-problems/{problem_id}",
    response_model=WrongProblemResponse,
    summary="更新错题",
)
def update_wrong_problem(
    problem_id: str,
    data: WrongProblemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WrongProblemResponse:
    """更新错题信息。"""
    problem = (
        db.query(WrongProblem)
        .filter(WrongProblem.id == problem_id, WrongProblem.user_id == current_user.id)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="错题不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(problem, key, value)

    db.commit()
    db.refresh(problem)
    return _problem_to_response(problem)


@router.delete(
    "/wrong-problems/{problem_id}",
    status_code=204,
    summary="删除错题",
)
def delete_wrong_problem(
    problem_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除指定的错题记录。"""
    problem = (
        db.query(WrongProblem)
        .filter(WrongProblem.id == problem_id, WrongProblem.user_id == current_user.id)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="错题不存在")

    db.delete(problem)
    db.commit()


# ─── OCR 识别 ─────────────────────────────────────────

@router.post(
    "/wrong-problems/ocr",
    response_model=OCRResponse,
    summary="OCR 识别图片文字",
    description="调用 PaddleOCR 服务识别试卷图片中的文字内容。",
)
def ocr_recognize(
    data: OCRRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OCRResponse:
    """对上传的图片进行 OCR 文字识别。"""
    # PaddleOCR 以独立 Docker 容器运行（fls-paddleocr:5000）
    # 这里通过 HTTP 调用 OCR 服务
    # TODO: Phase 2 完善后，改为异步任务队列
    import httpx

    try:
        minio_service = MinioService()
        image_bytes = minio_service.download_file(data.image_path)

        resp = httpx.post(
            "http://fls-paddleocr:5000/ocr",
            files={"image": ("image.jpg", image_bytes, "image/jpeg")},
            timeout=60.0,
        )
        resp.raise_for_status()
        result = resp.json()
        return OCRResponse(
            text=result.get("text", ""),
            confidence=result.get("confidence", 0.0),
            image_path=data.image_path,
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"OCR 服务不可用: {str(e)}"
        )


# ─── AI 评估 ──────────────────────────────────────────

@router.post(
    "/wrong-problems/evaluate",
    response_model=AIEvaluationResponse,
    summary="AI 评估作答",
    description="调用 LLM 评估学生作答是否正确，并给出分析。",
)
async def ai_evaluate(
    data: AIEvaluationRequest,
    current_user: User = Depends(get_current_user),
) -> AIEvaluationResponse:
    """AI 评估学生作答。"""
    result = await llm_service.evaluate_answer(
        problem_text=data.problem_text,
        student_answer=data.student_answer,
        subject=data.subject,
    )
    if not result:
        raise HTTPException(status_code=503, detail="AI 评估服务暂不可用")

    return AIEvaluationResponse(
        is_correct=result.get("is_correct", False),
        evaluation=result.get("evaluation", ""),
        correct_answer=result.get("correct_answer"),
    )


# ─── 解题生成 ─────────────────────────────────────────

@router.post(
    "/wrong-problems/solution",
    response_model=SolutionResponse,
    summary="生成解题过程",
    description="调用 LLM 生成详细的解题步骤和思路分析。",
)
async def generate_solution(
    data: SolutionRequest,
    current_user: User = Depends(get_current_user),
) -> SolutionResponse:
    """生成解题过程。"""
    result = await llm_service.generate_solution(
        problem_text=data.problem_text,
        subject=data.subject,
        knowledge_point=data.knowledge_point,
    )
    if not result:
        raise HTTPException(status_code=503, detail="解题生成服务暂不可用")

    return SolutionResponse(
        solution=result.get("solution", ""),
        approach=result.get("approach", ""),
    )


# ─── 自动收录 ─────────────────────────────────────────

@router.post(
    "/wrong-problems/auto-collect",
    response_model=AutoCollectResponse,
    summary="自动收录错题",
    description="一站式完成：图片上传 → OCR 识别 → AI 评估 → 自动创建错题记录。",
)
async def auto_collect(
    data: AutoCollectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AutoCollectResponse:
    """自动收录错题（OCR + AI 评估 + 入库）。"""
    # 1. OCR 识别
    import httpx

    try:
        minio_service = MinioService()
        image_bytes = minio_service.download_file(data.image_path)

        ocr_resp = httpx.post(
            "http://fls-paddleocr:5000/ocr",
            files={"image": ("image.jpg", image_bytes, "image/jpeg")},
            timeout=60.0,
        )
        ocr_resp.raise_for_status()
        ocr_result = ocr_resp.json()
        ocr_text = ocr_result.get("text", "")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="OCR 服务不可用")

    if not ocr_text.strip():
        raise HTTPException(status_code=400, detail="OCR 未识别到文字内容")

    # 2. AI 评估
    eval_result = await llm_service.evaluate_answer(
        problem_text=ocr_text,
        student_answer="",
        subject=data.subject,
    )
    evaluation_text = eval_result.get("evaluation", "") if eval_result else ""
    is_correct = 1 if eval_result and eval_result.get("is_correct", False) else 0

    # 3. 生成解题过程
    solution_result = await llm_service.generate_solution(
        problem_text=ocr_text,
        subject=data.subject,
        knowledge_point=data.knowledge_point,
    )
    solution_text = solution_result.get("solution", "") if solution_result else ""

    # 4. 创建错题记录
    problem = WrongProblem(
        user_id=current_user.id,
        subject=data.subject,
        knowledge_point=data.knowledge_point,
        problem_text=ocr_text,
        student_answer="",
        correct_answer=eval_result.get("correct_answer", "") if eval_result else "",
        ai_evaluation=evaluation_text,
        is_correct=is_correct,
        solution=solution_text,
        image_path=data.image_path,
        difficulty=1,
        wrong_count=1 if is_correct == 0 else 0,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)

    return AutoCollectResponse(
        wrong_problem=_problem_to_response(problem),
        ocr_text=ocr_text,
        evaluation=evaluation_text,
        is_correct=is_correct == 1,
    )
