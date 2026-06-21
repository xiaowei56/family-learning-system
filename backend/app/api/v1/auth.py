"""
认证模块 API 路由

提供用户注册和登录接口，使用 JWT 令牌进行身份认证。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建新用户账号，返回用户基本信息。用户名需唯一，密码至少 6 位。",
    responses={
        201: {"description": "注册成功"},
        409: {"description": "用户名已存在"},
    },
)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    """
    用户注册。

    - **username**: 用户名（唯一，2-50 字符）
    - **password**: 密码（至少 6 字符）
    - **role**: 角色（parent / student，默认为 parent）
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"用户名 '{request.username}' 已被注册",
        )

    # 创建用户
    new_user = User(
        username=request.username,
        hashed_password=hash_password(request.password),
        role=request.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RegisterResponse(
        id=str(new_user.id),
        username=new_user.username,
        role=new_user.role,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="用户登录",
    description="使用用户名和密码登录，返回 JWT 访问令牌。",
    responses={
        200: {"description": "登录成功"},
        401: {"description": "用户名或密码错误"},
    },
)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """
    用户登录。

    - **username**: 用户名
    - **password**: 密码
    """
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 验证密码
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 检查账号是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号已被禁用",
        )

    # 生成 JWT 令牌
    access_token = create_access_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            role=user.role,
        ),
    )
