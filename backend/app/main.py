"""
家庭学习系统 — FastAPI 主应用

提供健康检查、CORS 中间件、JWT 认证中间件（占位），
以及 API 路由挂载。
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

# ─── 创建 FastAPI 实例 ──────────────────────────────
app = FastAPI(
    title="家庭学习系统 API",
    description="面向 K12 学生的家庭学习辅助系统后端接口",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ─── CORS 中间件 ────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── JWT 认证中间件占位 ────────────────────────────
@app.middleware("http")
async def jwt_auth_middleware(request: Request, call_next):
    """
    JWT 认证中间件（占位）。

    跳过 /health、/docs、/openapi.json、/api/v1/auth/ 路径的认证校验。
    后续实现认证模块后，在此处解析 Authorization Header 中的 JWT Token，
    并将当前用户信息注入 request.state.user。
    """
    # 免认证路径
    public_paths = {"/health", "/docs", "/redoc", "/openapi.json"}
    if request.url.path in public_paths or request.url.path.startswith("/api/v1/auth/"):
        return await call_next(request)

    # TODO: JWT 认证校验（Phase 1 实现）
    # authorization = request.headers.get("Authorization")
    # if not authorization or not authorization.startswith("Bearer "):
    #     return JSONResponse(status_code=401, content={"detail": "未提供认证令牌"})
    # try:
    #     payload = decode_jwt(authorization.split(" ")[1])
    #     request.state.user = payload
    # except JWTError:
    #     return JSONResponse(status_code=401, content={"detail": "无效的认证令牌"})

    response = await call_next(request)
    return response


# ─── 健康检查 ────────────────────────────────────────
@app.get("/health")
async def health_check():
    """
    健康检查端点。

    返回服务运行状态，供 Nginx / Docker Compose 健康检查使用。
    后续可扩展为检查各服务连接状态（PostgreSQL / MinIO / Redis）。
    """
    return JSONResponse(
        content={
            "status": "ok",
            "service": "family-learning-system",
            "version": "0.1.0",
        }
    )


# ─── API 路由挂载 ────────────────────────────────────
from app.api.v1 import router as v1_router

app.include_router(v1_router, prefix="/api/v1")
