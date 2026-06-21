"""
家庭学习系统 — 全局配置

所有配置项优先从环境变量读取，提供合理默认值（内网开发环境）。
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ─── FastAPI ────────────────────────────────────
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    log_level: str = "info"

    # ─── PostgreSQL ─────────────────────────────────
    database_url: str = "postgresql://fls_user:fls_password@postgres:5432/family_learning"

    # ─── MinIO 对象存储 ─────────────────────────────
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "fls_minio_admin"
    minio_secret_key: str = "fls_minio_password"
    minio_bucket_name: str = "family-learning-images"
    minio_secure: bool = False  # 内网不启用 TLS

    # ─── Redis ──────────────────────────────────────
    redis_url: str = "redis://redis:6379/0"

    # ─── LLM API ────────────────────────────────────
    llm_api_url: str = "http://192.168.110.7/v1"
    llm_api_key: str = ""  # 本地 API 可能不需要 key
    llm_model: str = "default"

    # ─── JWT ────────────────────────────────────────
    jwt_secret: str = "family-learning-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # ─── CORS ───────────────────────────────────────
    cors_origins: list[str] = ["*"]  # 内网环境，允许所有来源

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
