"""
Alembic 迁移环境配置

从 app.core.database 导入 Base 和 engine，
让 Alembic 自动发现所有已注册的 SQLAlchemy 模型。
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.core.database import Base

# 导入所有模型以确保它们注册到 Base.metadata
import app.models  # noqa: F401

# Alembic Config 对象
config = context.config

# 从 settings 中读取数据库 URL
config.set_main_option("sqlalchemy.url", settings.database_url)

# 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标元数据 —— Alembic 自动对比此元数据与数据库生成迁移
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    离线模式运行迁移（仅生成 SQL 脚本，不连接数据库）。

    适用于 CI/CD 审查迁移 SQL 的场景。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在线模式运行迁移（连接数据库执行迁移）。

    开发环境直接使用此模式。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
