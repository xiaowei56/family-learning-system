"""
学生档案 API 路由

提供学生档案的增删改查功能，所有接口需要 JWT 认证。
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.student import Student
from app.models.user import User
from app.schemas.student import (
    StudentCreateRequest,
    StudentResponse,
    StudentUpdateRequest,
)

router = APIRouter(prefix="/students", tags=["学生档案"])


@router.get(
    "",
    response_model=List[StudentResponse],
    summary="获取学生列表",
    description="获取当前用户创建的所有学生档案列表。",
)
def list_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[StudentResponse]:
    """获取当前用户的所有学生档案。"""
    students = (
        db.query(Student)
        .filter(Student.user_id == current_user.id)
        .order_by(Student.created_at.desc())
        .all()
    )

    return [
        StudentResponse(
            id=str(s.id),
            user_id=str(s.user_id),
            name=s.name,
            grade_level=s.grade_level,
            avatar=s.avatar,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in students
    ]


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建学生档案",
    description="为当前用户创建新的学生档案。",
    responses={
        201: {"description": "创建成功"},
    },
)
def create_student(
    request: StudentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentResponse:
    """创建学生档案。"""
    student = Student(
        user_id=current_user.id,
        name=request.name,
        grade_level=request.grade_level,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return StudentResponse(
        id=str(student.id),
        user_id=str(student.user_id),
        name=student.name,
        grade_level=student.grade_level,
        avatar=student.avatar,
        created_at=student.created_at,
        updated_at=student.updated_at,
    )


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="更新学生档案",
    description="更新指定学生档案的信息（姓名、年级、头像）。",
    responses={
        200: {"description": "更新成功"},
        404: {"description": "学生档案不存在"},
        403: {"description": "无权操作该学生档案"},
    },
)
def update_student(
    student_id: UUID,
    request: StudentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentResponse:
    """更新学生档案。"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生档案不存在",
        )

    # 验证所有权
    if student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该学生档案",
        )

    # 更新字段（仅更新非 None 的字段）
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return StudentResponse(
        id=str(student.id),
        user_id=str(student.user_id),
        name=student.name,
        grade_level=student.grade_level,
        avatar=student.avatar,
        created_at=student.created_at,
        updated_at=student.updated_at,
    )


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除学生档案",
    description="删除指定的学生档案。",
    responses={
        204: {"description": "删除成功"},
        404: {"description": "学生档案不存在"},
        403: {"description": "无权操作该学生档案"},
    },
)
def delete_student(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除学生档案。"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学生档案不存在",
        )

    # 验证所有权
    if student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该学生档案",
        )

    db.delete(student)
    db.commit()
