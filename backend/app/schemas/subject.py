"""
科目模块 Pydantic 模式

定义科目列表查询和用户科目配置接口的数据结构。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SubjectResponse(BaseModel):
    """科目响应体"""

    id: str = Field(..., description="科目 ID")
    name: str = Field(..., description="科目名称", examples=["数学"])
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class UserSubjectsRequest(BaseModel):
    """用户设置科目请求体"""

    subject_ids: list[str] = Field(
        ...,
        min_length=1,
        description="科目 ID 列表",
        examples=[["uuid1", "uuid2"]],
    )


class UserSubjectItem(BaseModel):
    """用户已选科目项"""

    id: str = Field(..., description="关联记录 ID")
    subject_id: str = Field(..., description="科目 ID")
    subject_name: str = Field(..., description="科目名称")

    model_config = {"from_attributes": True}


class UserSubjectsResponse(BaseModel):
    """用户已选科目响应体"""

    subjects: list[UserSubjectItem] = Field(
        ..., description="用户已选科目列表"
    )
