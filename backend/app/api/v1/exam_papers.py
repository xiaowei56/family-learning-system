"""
试卷整理 API 路由

提供试卷上传归档、查询、笔迹擦除和题目标注功能。
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_student_ownership
from app.models.user import User
from app.models.exam_paper import ExamPaper, PaperAnnotation
from app.schemas.exam_paper import (
    EraseHandwritingRequest,
    EraseHandwritingResponse,
    ExamPaperCreate,
    ExamPaperListResponse,
    ExamPaperResponse,
    ExamPaperUpdate,
    PaperAnnotationCreate,
    PaperAnnotationResponse,
)
from app.services.minio_client import MinioService

router = APIRouter(tags=["试卷整理"])


def _paper_to_response(p: ExamPaper) -> ExamPaperResponse:
    return ExamPaperResponse(
        id=str(p.id),
        user_id=str(p.user_id),
        subject=p.subject,
        title=p.title,
        exam_type=p.exam_type,
        exam_date=p.exam_date,
        original_image_path=p.original_image_path,
        clean_image_path=p.clean_image_path,
        ocr_text=p.ocr_text,
        student_id=str(p.student_id) if p.student_id else None,
        page_count=p.page_count,
        status=p.status,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


# ─── 试卷 CRUD ────────────────────────────────────────

@router.get(
    "/exam-papers",
    response_model=ExamPaperListResponse,
    summary="获取试卷列表",
    description="按科目、考试类型、日期范围等条件查询试卷列表。",
)
def list_exam_papers(
    subject: Optional[str] = Query(None, description="科目筛选"),
    exam_type: Optional[str] = Query(None, description="考试类型"),
    status: Optional[str] = Query(None, description="状态筛选"),
    student_id: Optional[str] = Query(None, description="所属学生 ID 筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExamPaperListResponse:
    """获取当前用户的试卷列表。"""
    verify_student_ownership(student_id, current_user, db)
    query = db.query(ExamPaper).filter(ExamPaper.user_id == current_user.id)

    if subject:
        query = query.filter(ExamPaper.subject == subject)
    if exam_type:
        query = query.filter(ExamPaper.exam_type == exam_type)
    if status:
        query = query.filter(ExamPaper.status == status)
    if student_id:
        query = query.filter(ExamPaper.student_id == student_id)

    total = query.count()
    items = (
        query.order_by(ExamPaper.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ExamPaperListResponse(
        items=[_paper_to_response(p) for p in items],
        total=total,
    )


@router.get(
    "/exam-papers/{paper_id}",
    response_model=ExamPaperResponse,
    summary="获取试卷详情",
)
def get_exam_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExamPaperResponse:
    """获取单份试卷的详细信息。"""
    paper = (
        db.query(ExamPaper)
        .filter(ExamPaper.id == paper_id, ExamPaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    return _paper_to_response(paper)


@router.post(
    "/exam-papers",
    response_model=ExamPaperResponse,
    status_code=201,
    summary="上传并创建试卷",
)
def create_exam_paper(
    data: ExamPaperCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExamPaperResponse:
    """上传试卷图片并创建试卷记录。"""
    verify_student_ownership(data.student_id, current_user, db)
    paper = ExamPaper(
        user_id=current_user.id,
        student_id=data.student_id,
        subject=data.subject,
        title=data.title,
        exam_type=data.exam_type,
        exam_date=data.exam_date,
        original_image_path=data.image_path,
        page_count=data.page_count or 1,
        status="uploaded",
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return _paper_to_response(paper)


@router.put(
    "/exam-papers/{paper_id}",
    response_model=ExamPaperResponse,
    summary="更新试卷信息",
)
def update_exam_paper(
    paper_id: str,
    data: ExamPaperUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExamPaperResponse:
    """更新试卷信息。"""
    paper = (
        db.query(ExamPaper)
        .filter(ExamPaper.id == paper_id, ExamPaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(paper, key, value)

    db.commit()
    db.refresh(paper)
    return _paper_to_response(paper)


@router.delete(
    "/exam-papers/{paper_id}",
    status_code=204,
    summary="删除试卷",
)
def delete_exam_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除试卷及所有标注。"""
    paper = (
        db.query(ExamPaper)
        .filter(ExamPaper.id == paper_id, ExamPaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")

    # 可选：删除 MinIO 中的图片文件
    db.delete(paper)
    db.commit()


# ─── 图片上传 ─────────────────────────────────────────

@router.post(
    "/exam-papers/upload",
    summary="上传试卷图片",
    description="上传试卷图片到 MinIO，支持多页试卷。",
)
async def upload_paper_image(
    file: UploadFile = File(..., description="试卷图片"),
    current_user: User = Depends(get_current_user),
) -> dict:
    """上传试卷图片到 MinIO 存储。"""
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="仅支持 JPEG 和 PNG 格式")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 50MB")

    filename = f"exam_papers/{current_user.id}/{uuid.uuid4().hex}_{file.filename}"
    minio_service = MinioService()
    url = minio_service.upload_file(content, filename, content_type=file.content_type)

    return {"image_path": filename, "url": url}


# ─── OCR 识别试卷 ─────────────────────────────────────

@router.post(
    "/exam-papers/{paper_id}/ocr",
    response_model=ExamPaperResponse,
    summary="OCR 识别整卷",
    description="对试卷进行整卷 OCR 识别，更新试卷状态。",
)
def ocr_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExamPaperResponse:
    """对试卷图片进行 OCR 识别。"""
    paper = (
        db.query(ExamPaper)
        .filter(ExamPaper.id == paper_id, ExamPaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")

    # 调用 PaddleOCR 服务
    import httpx

    try:
        minio_service = MinioService()
        image_bytes = minio_service.download_file(paper.original_image_path)

        resp = httpx.post(
            "http://fls-paddleocr:5000/ocr",
            files={"image": ("image.jpg", image_bytes, "image/jpeg")},
            timeout=120.0,
        )
        resp.raise_for_status()
        result = resp.json()
        paper.ocr_text = result.get("text", "")
        paper.status = "ocr_done"
        db.commit()
        db.refresh(paper)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"OCR 服务不可用: {str(e)}")

    return _paper_to_response(paper)


# ─── 笔迹擦除 ─────────────────────────────────────────

@router.post(
    "/exam-papers/{paper_id}/erase",
    response_model=EraseHandwritingResponse,
    summary="擦除笔迹",
    description="对试卷图片进行笔迹擦除处理，生成洁净版。",
)
def erase_handwriting(
    paper_id: str,
    data: EraseHandwritingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EraseHandwritingResponse:
    """擦除试卷上的手写笔迹。"""
    paper = (
        db.query(ExamPaper)
        .filter(ExamPaper.id == paper_id, ExamPaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")

    # TODO: Phase 2 完善后接入图像修复（inpainting）模型
    # 当前返回占位，直接使用原图
    clean_path = paper.original_image_path.replace(
        ".jpg", "_clean.jpg"
    ).replace(".png", "_clean.png")

    paper.clean_image_path = clean_path
    paper.status = "cleaned"
    db.commit()
    db.refresh(paper)

    return EraseHandwritingResponse(
        clean_image_path=clean_path,
        status="cleaned",
    )


# ─── 试卷标注 ─────────────────────────────────────────

@router.get(
    "/exam-papers/{paper_id}/annotations",
    response_model=list[PaperAnnotationResponse],
    summary="获取试卷标注列表",
)
def list_annotations(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PaperAnnotationResponse]:
    """获取试卷的所有标注。"""
    paper = (
        db.query(ExamPaper)
        .filter(ExamPaper.id == paper_id, ExamPaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")

    annotations = (
        db.query(PaperAnnotation)
        .filter(PaperAnnotation.paper_id == paper_id)
        .order_by(PaperAnnotation.created_at.asc())
        .all()
    )

    return [
        PaperAnnotationResponse(
            id=str(a.id),
            paper_id=str(a.paper_id),
            annotation_type=a.annotation_type,
            position=a.position,
            content=a.content,
            color=a.color,
            created_at=a.created_at,
        )
        for a in annotations
    ]


@router.post(
    "/exam-papers/{paper_id}/annotations",
    response_model=PaperAnnotationResponse,
    status_code=201,
    summary="添加标注",
)
def create_annotation(
    paper_id: str,
    data: PaperAnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaperAnnotationResponse:
    """在试卷上添加标注。"""
    paper = (
        db.query(ExamPaper)
        .filter(ExamPaper.id == paper_id, ExamPaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")

    annotation = PaperAnnotation(
        paper_id=paper.id,
        annotation_type=data.annotation_type,
        position=data.position,
        content=data.content,
        color=data.color or "#ff0000",
    )
    db.add(annotation)
    db.commit()
    db.refresh(annotation)

    paper.status = "annotated"
    db.commit()

    return PaperAnnotationResponse(
        id=str(annotation.id),
        paper_id=str(annotation.paper_id),
        annotation_type=annotation.annotation_type,
        position=annotation.position,
        content=annotation.content,
        color=annotation.color,
        created_at=annotation.created_at,
    )


@router.delete(
    "/exam-papers/{paper_id}/annotations/{annotation_id}",
    status_code=204,
    summary="删除标注",
)
def delete_annotation(
    paper_id: str,
    annotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除指定的标注。"""
    annotation = (
        db.query(PaperAnnotation)
        .filter(
            PaperAnnotation.id == annotation_id,
            PaperAnnotation.paper_id == paper_id,
        )
        .first()
    )
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")

    # 验证试卷归属
    paper = (
        db.query(ExamPaper)
        .filter(ExamPaper.id == paper_id, ExamPaper.user_id == current_user.id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")

    db.delete(annotation)
    db.commit()
