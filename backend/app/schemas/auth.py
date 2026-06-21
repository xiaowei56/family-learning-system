"""
认证模块 Pydantic 模式

定义注册/登录接口的请求体和响应体数据结构与校验规则。
"""

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    """用户注册请求体"""

    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="用户名，2-50 个字符",
        examples=["zhangsan"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="密码，6-128 个字符",
        examples=["securepassword"],
    )
    role: str = Field(
        default="parent",
        pattern=r"^(parent|student)$",
        description="用户角色：parent（家长）/ student（学生）",
        examples=["parent"],
    )

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码长度不能少于 6 个字符")
        return v


class LoginRequest(BaseModel):
    """用户登录请求体"""

    username: str = Field(
        ...,
        min_length=1,
        description="用户名",
        examples=["zhangsan"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="密码",
        examples=["securepassword"],
    )


class UserResponse(BaseModel):
    """用户基本信息响应体"""

    id: str = Field(..., description="用户 ID", examples=["uuid-string"])
    username: str = Field(..., description="用户名", examples=["zhangsan"])
    role: str = Field(..., description="用户角色", examples=["parent"])

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    """注册成功响应体"""

    id: str = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """登录成功响应体"""

    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="当前登录用户信息")


class ErrorResponse(BaseModel):
    """通用错误响应体"""

    detail: str = Field(..., description="错误详情")
