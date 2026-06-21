"""
数据库连接与会话管理

使用 SQLAlchemy 2.0 异步风格（同步版本）。
后续可迁移至 async 版本提升并发性能。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# ─── 数据库引擎 ──────────────────────────────────────
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# ─── 会话工厂 ────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── 声明基类 ────────────────────────────────────────
class Base(DeclarativeBase):
    """所有 SQLAlchemy 模型的基类。"""
    pass


# ─── 依赖注入 ────────────────────────────────────────
def get_db():
    """
    FastAPI 依赖 —— 获取数据库会话。

    使用方式：
        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── 初始化数据库表 ─────────────────────────────────
def init_db():
    """
    创建所有尚未存在的数据库表。
    可通过 `make db-migrate` 或 `python -m app.core.database` 调用。
    """
    from app.models import Base  # noqa: F401 — 确保所有模型已导入

    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表初始化完成")


if __name__ == "__main__":
    init_db()
