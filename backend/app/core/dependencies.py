"""
FastAPI 依赖注入工具

提供 JWT 令牌创建/验证、当前用户获取等通用依赖。
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import get_db
from app.models.user import User

# ─── 密码加密 ────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── HTTP Bearer 令牌提取 ────────────────────────────
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希。"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否匹配哈希值。"""
    return pwd_context.verify(plain_password, hashed_password)


# ─── JWT 令牌 ────────────────────────────────────────
def create_access_token(data: dict) -> str:
    """
    创建 JWT 访问令牌。

    Args:
        data: 包含用户信息的字典（至少需含 "sub" 字段）

    Returns:
        编码后的 JWT 字符串
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """
    解码并验证 JWT 令牌。

    Args:
        token: JWT 字符串

    Returns:
        解码后的 payload 字典；验证失败返回 None
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


# ─── 获取当前用户依赖 ────────────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    从 JWT 令牌解析当前登录用户。

    流程：
        1. 从 Authorization Header 提取 Bearer Token
        2. 解码并验证 JWT 签名与过期时间
        3. 根据 sub（用户 ID）从数据库查询用户
        4. 返回 User 对象，或抛出 401 异常

    Raises:
        HTTPException(401): 令牌无效、过期、或用户不存在/已禁用
    """
    token = credentials.credentials

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌中缺少用户标识",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
