"""
学生档案模块 Pydantic 模式

定义学生档案 CRUD 接口的请求体和响应体数据结构与校验规则。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    """创建学生档案请求体"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="学生姓名",
        examples=["小明"],
    )
    grade_level: str = Field(
        ...,
        pattern=r"^(小学|初中|高中)$",
        description="年级：小学 / 初中 / 高中",
        examples=["小学"],
    )


class StudentUpdateRequest(BaseModel):
    """更新学生档案请求体（全部可选）"""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="学生姓名",
        examples=["小明"],
    )
    grade_level: Optional[str] = Field(
        None,
        pattern=r"^(小学|初中|高中)$",
        description="年级：小学 / 初中 / 高中",
        examples=["初中"],
    )
    avatar: Optional[str] = Field(
        None,
        description="头像 URL",
        examples=["http://minio:9000/bucket/avatars/xxx.jpg"],
    )


class StudentResponse(BaseModel):
    """学生档案响应体"""

    id: str = Field(..., description="学生档案 ID")
    user_id: str = Field(..., description="所属家长用户 ID")
    name: str = Field(..., description="学生姓名")
    grade_level: str = Field(..., description="年级")
    avatar: Optional[str] = Field(None, description="头像 URL")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    model_config = {"from_attributes": True}
