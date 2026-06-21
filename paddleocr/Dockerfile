# PaddleOCR 服务镜像
# 基于 PaddlePaddle CPU 镜像，封装为 REST API 供主应用调用

FROM paddlepaddle/paddle:3.0.0rc0

LABEL maintainer="family-learning-system"

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip install --no-cache-dir \
    flask==3.0.3 \
    gunicorn==22.0.0 \
    paddleocr==2.9.1 \
    -i https://mirror.baidu.com/pypi/simple

# 创建应用目录
WORKDIR /app

# 复制服务代码
COPY server.py .

# 下载并缓存 OCR 模型（首次启动时自动下载）
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)" || true

# 暴露端口
EXPOSE 5000

# 启动服务
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "server:app"]
