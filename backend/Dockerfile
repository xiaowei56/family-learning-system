FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（psycopg2 需要 libpq）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建静态文件目录
RUN mkdir -p /app/static

EXPOSE 8000

# 使用 uvicorn 启动 FastAPI 应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
