"""
Pydantic 数据模式包

定义 API 请求/响应的数据结构和校验规则。
"""

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from app.schemas.student import (
    StudentCreateRequest,
    StudentResponse,
    StudentUpdateRequest,
)
from app.schemas.subject import (
    SubjectResponse,
    UserSubjectsRequest,
    UserSubjectsResponse,
)
from app.schemas.exam_result import (
    ExamResultCreate,
    ExamResultResponse,
    ExamResultUpdate,
    SummaryResponse,
    TrendResponse,
)

__all__ = [
    "RegisterRequest",
    "RegisterResponse",
    "LoginRequest",
    "LoginResponse",
    "UserResponse",
    "StudentCreateRequest",
    "StudentUpdateRequest",
    "StudentResponse",
    "SubjectResponse",
    "UserSubjectsRequest",
    "UserSubjectsResponse",
    "ExamResultCreate",
    "ExamResultUpdate",
    "ExamResultResponse",
    "TrendResponse",
    "SummaryResponse",
]
