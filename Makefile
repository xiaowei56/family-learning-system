.PHONY: dev build logs db-migrate down restart ps shell

# 启动所有服务（后台运行）
dev:
	docker compose up -d

# 构建/重新构建镜像
build:
	docker compose build

# 查看所有服务日志（实时跟踪）
logs:
	docker compose logs -f

# 执行数据库迁移（初始化数据库表结构）
db-migrate:
	docker compose exec fastapi python -m app.core.database

# 停止所有服务
down:
	docker compose down

# 重启指定服务（如 make restart service=fastapi）
restart:
	docker compose restart $(service)

# 查看服务状态
ps:
	docker compose ps

# 进入指定容器的 shell
shell:
	docker compose exec $(service) sh
