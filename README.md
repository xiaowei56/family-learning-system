# 家庭学习系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)]()

面向 K12 学生的家庭学习辅助系统，部署在家庭 NAS 局域网内使用。支持 **Web 端** 和 **Android 端（Flutter）**，涵盖学习记录、艾宾浩斯复习提醒、试卷 OCR 识别、错题本、AI 智能评估、薄弱点分析与智能出卷等核心功能。所有 AI 推理基于本地 LLM API，数据完全内网存储，无需连接公网。

---

## 特性

- **学习记录与记忆曲线** — 记录每日学习笔记，基于艾宾浩斯遗忘曲线自动生成复习计划，支持调速和标记已掌握
- **考试成绩追踪** — 记录各科目考试成绩，自动计算得分率，提供多科目趋势对比图表（ECharts）
- **试卷 OCR 识别** — 拍照上传试卷，PaddleOCR 识别文字，AI 自动评估作答正误并生成解题过程
- **错题本** — 自动收录错题，按科目/知识点/难度筛选，支持查看 AI 评估和解题步骤
- **举一反三** — 基于错题调用 LLM 生成相似练习题，巩固薄弱知识点
- **薄弱点分析** — 聚合错题与考试成绩，生成掌握度雷达图，提供学习诊断报告
- **智能出卷** — 针对薄弱知识点调用 LLM 生成针对性练习试卷，支持难度分布
- **纯内网部署** — 所有数据存储在本地 PostgreSQL + MinIO，AI 推理使用局域网 LLM API

---

## 技术栈

| 层 | 技术 | 用途 |
|---|---|---|
| **后端框架** | Python FastAPI 0.111 | REST API |
| **ORM** | SQLAlchemy 2.0 + Alembic | 数据模型与迁移 |
| **数据库** | PostgreSQL 16 | 业务数据持久化 |
| **对象存储** | MinIO | 试卷/错题图片存储 |
| **缓存** | Redis 7 | Session/缓存 |
| **OCR** | PaddleOCR 2.9 | 图片文字识别 |
| **AI 推理** | 本地 LLM API (OpenAI 兼容) | 作答评估/解题生成/出卷 |
| **前端** | Vue 3 + Element Plus + Vite | Web 管理界面 |
| **图表** | ECharts 5.5 | 雷达图/趋势图 |
| **网关** | Nginx | 反向代理/静态资源 |
| **容器** | Docker Compose | 一键部署 |
| **Android** | Flutter（TBD） | 移动端 |

---

## 快速开始

### 环境要求

- Docker & Docker Compose v2
- 局域网内可访问的 LLM API（兼容 OpenAI 格式）
- 最低配置：4 核 CPU、8 GB 内存、50 GB 磁盘

### 1. 克隆项目

```bash
git clone <your-repo-url> studyhome
cd studyhome
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，重点修改以下项：

| 变量 | 说明 | 默认值 |
|---|---|---|
| `POSTGRES_PASSWORD` | 数据库密码 | `fls_password` |
| `MINIO_ROOT_PASSWORD` | MinIO 管理员密码 | `fls_minio_password` |
| `LLM_API_URL` | 本地 LLM API 地址 | `http://192.168.110.7/v1` |
| `JWT_SECRET` | JWT 签名密钥 | `family-learning-jwt-secret-change-in-production` |

### 3. 启动服务

```bash
make dev
```

或手动执行：

```bash
docker compose up -d
```

首次启动会自动构建镜像并初始化数据库表结构。

### 4. 访问服务

| 服务 | 地址 |
|---|---|
| Web 前端 | `http://<host>/` |
| API 文档 | `http://<host>/docs` |
| MinIO 控制台 | `http://<host>/minio-console/` |

### 5. 注册账号

打开浏览器访问首页，点击「注册」创建家庭账号，登录后即可使用。

---

## 项目结构

```
studyhome/
├── backend/                        # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/                 # API 路由
│   │   │   ├── auth.py             # 认证（注册/登录/JWT）
│   │   │   ├── students.py         # 学生档案
│   │   │   ├── subjects.py         # 科目配置
│   │   │   ├── study_records.py    # 学习记录 + 复习计划
│   │   │   ├── exam_results.py     # 考试成绩 + 趋势图
│   │   │   ├── dashboard.py        # 首页摘要
│   │   │   ├── wrong_problems.py   # 错题管理（OCR/评估/收录）
│   │   │   ├── exam_papers.py      # 试卷整理（CRUD/擦除/标注）
│   │   │   ├── similar_problems.py # 举一反三
│   │   │   └── weak_points.py      # 薄弱点分析 + 智能出卷
│   │   ├── core/
│   │   │   ├── database.py         # 数据库连接
│   │   │   └── dependencies.py     # JWT/密码/当前用户
│   │   ├── models/                 # SQLAlchemy ORM 模型
│   │   │   ├── user.py
│   │   │   ├── student.py
│   │   │   ├── subject.py
│   │   │   ├── study_record.py
│   │   │   ├── exam_result.py
│   │   │   ├── wrong_problem.py
│   │   │   ├── exam_paper.py
│   │   │   └── advanced_analysis.py
│   │   ├── schemas/               # Pydantic 请求/响应模型
│   │   ├── services/
│   │   │   ├── memory_curve.py     # 艾宾浩斯遗忘曲线算法
│   │   │   ├── minio_client.py     # MinIO 对象存储
│   │   │   └── llm_service.py      # LLM API 调用封装
│   │   ├── config.py               # 全局配置
│   │   └── main.py                 # 应用入口
│   ├── alembic/                    # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
│
├── web/                            # Vue3 前端
│   ├── src/
│   │   ├── api/index.js            # Axios 封装 + JWT 拦截器
│   │   ├── router/index.js         # 路由配置
│   │   └── views/                  # 10 个页面组件
│   │       ├── Login.vue           # 登录/注册
│   │       ├── Dashboard.vue       # 首页（统计卡片）
│   │       ├── StudyRecords.vue    # 学习记录
│   │       ├── ReviewCenter.vue    # 复习中心
│   │       ├── ExamScores.vue      # 考试成绩（含 ECharts 趋势图）
│   │       ├── WrongProblems.vue   # 错题本（拍照收录/AI 评估）
│   │       ├── PaperLibrary.vue    # 试卷库（上传/OCR）
│   │       ├── SimilarProblems.vue # 举一反三
│   │       ├── WeakPoints.vue      # 薄弱点分析（雷达图/出卷）
│   │       └── Settings.vue        # 设置
│   ├── package.json
│   └── vite.config.js
│
├── paddleocr/                      # PaddleOCR 独立服务
│   ├── Dockerfile
│   └── server.py                   # Flask REST API 封装
│
├── nginx/
│   └── default.conf                # 反向代理配置
│
├── docker-compose.yml              # 编排所有服务
├── Makefile                        # 常用命令
├── .env.example                    # 环境变量模板
└── 家庭学习系统-需求规格.md          # 完整需求文档
```

---

## API 概览

所有 API 前缀为 `/api/v1`，需要鉴权的接口在 Header 中携带 `Authorization: Bearer <token>`。

### 认证模块

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录（返回 JWT） |
| GET | `/api/v1/students` | 获取学生档案 |
| PUT | `/api/v1/students` | 更新学生档案 |
| GET | `/api/v1/subjects` | 获取科目列表 |
| POST | `/api/v1/users/me/subjects` | 配置个人科目 |

### 学习记录

| 方法 | 路径 | 说明 |
|---|---|---|
| GET/POST | `/api/v1/study-records` | 学习记录列表/创建 |
| PUT/DELETE | `/api/v1/study-records/{id}` | 更新/删除学习记录 |
| GET | `/api/v1/reviews/today` | 今日待复习列表（按科目分组） |
| PUT | `/api/v1/reviews/{id}/master` | 标记已掌握 |
| PUT | `/api/v1/reviews/{id}/speed` | 调整复习速度 |

### 考试成绩

| 方法 | 路径 | 说明 |
|---|---|---|
| GET/POST | `/api/v1/exam-results` | 成绩列表/录入 |
| DELETE | `/api/v1/exam-results/{id}` | 删除成绩 |
| GET | `/api/v1/exam-results/trend` | 多科目得分率趋势 |
| GET | `/api/v1/exam-results/summary` | 成绩摘要统计 |

### 错题管理

| 方法 | 路径 | 说明 |
|---|---|---|
| GET/POST | `/api/v1/wrong-problems` | 错题列表/手动录入 |
| GET/PUT/DELETE | `/api/v1/wrong-problems/{id}` | 错题详情/更新/删除 |
| POST | `/api/v1/wrong-problems/upload` | 上传图片到 MinIO |
| POST | `/api/v1/wrong-problems/ocr` | OCR 识别图片文字 |
| POST | `/api/v1/wrong-problems/evaluate` | AI 评估作答 |
| POST | `/api/v1/wrong-problems/solution` | 生成解题过程 |
| POST | `/api/v1/wrong-problems/auto-collect` | 自动收录错题（OCR+评估+入库） |

### 试卷整理

| 方法 | 路径 | 说明 |
|---|---|---|
| GET/POST | `/api/v1/exam-papers` | 试卷列表/创建 |
| GET/PUT/DELETE | `/api/v1/exam-papers/{id}` | 试卷详情/更新/删除 |
| POST | `/api/v1/exam-papers/upload` | 上传试卷图片 |
| POST | `/api/v1/exam-papers/{id}/ocr` | OCR 识别整卷 |
| POST | `/api/v1/exam-papers/{id}/erase` | 笔迹擦除 |
| GET/POST/DELETE | `/api/v1/exam-papers/{id}/annotations` | 题目标注 |

### 薄弱点与智能出卷

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/weak-points` | 薄弱点列表 |
| POST | `/api/v1/weak-points/analyze` | 执行薄弱点分析 |
| GET/POST | `/api/v1/practice-papers` | 练习试卷列表/生成 |
| PUT | `/api/v1/practice-papers/{id}/status` | 更新练习状态 |
| GET | `/api/v1/learning-advice` | 获取最新诊断报告 |
| GET/POST | `/api/v1/similar-problems` | 相似题列表/生成 |
| PUT | `/api/v1/similar-problems/{id}/practice` | 标记已练习 |

### 仪表盘

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/dashboard` | 首页摘要（今日复习/得分率/错题统计） |

---

## 开发指南

### 后端开发

```bash
# 进入后端容器
docker compose exec fastapi sh

# 手动运行数据库迁移
make db-migrate

# 查看 API 日志
make logs

# 重启后端服务（修改代码后）
make restart service=fastapi
```

修改后端代码后，由于 `docker-compose.yml` 中挂载了 `./backend:/app`，FastAPI 的 uvicorn 在 `--reload` 模式下会自动热重载。

### 前端开发

```bash
cd web

# 安装依赖
npm install

# 启动开发服务器（热重载，代理 API 到 8000 端口）
npm run dev

# 生产构建
npm run build
```

前端开发服务器运行在 `5173` 端口，通过 `vite.config.js` 配置的 proxy 将 `/api` 请求代理到后端 `8000` 端口。

### 数据库迁移

```bash
# Alembic 自动生成迁移
docker compose exec fastapi alembic revision --autogenerate -m "description"

# 执行迁移
docker compose exec fastapi alembic upgrade head

# 回滚迁移
docker compose exec fastapi alembic downgrade -1
```

---

## 部署架构

```
                        ┌──────────────┐
                        │   Nginx:80   │
                        │  反向代理    │
                        └──────┬───────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
         ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
         │  FastAPI  │  │   MinIO   │  │ PaddleOCR │
         │  :8000    │  │  :9000    │  │  :5000    │
         └─────┬─────┘  └───────────┘  └───────────┘
               │
        ┌──────┴──────┐
   ┌────▼────┐  ┌────▼────┐
   │PostgreSQL│  │  Redis  │
   │  :5432   │  │  :6379  │
   └─────────┘  └─────────┘
```

所有服务通过 Docker Compose 编排，运行在同一个 `internal` 网络中，通过服务名互相通信。Nginx 作为统一入口，对外暴露 80 端口。

---

## 常见问题

### OCR 服务无法启动

PaddleOCR 首次启动时需要下载模型文件（约 200 MB），请确保网络可访问百度镜像源。如果下载失败，可以手动下载模型文件放置到 `~/.paddleocr/` 目录。

### LLM API 连接失败

请确认 `LLM_API_URL` 配置正确（从**容器内部**能否访问宿主机？）。如果 LLM 服务在宿主机上运行，Docker 容器内需要使用 `host.docker.internal` 或宿主机内网 IP 来访问。

示例：`LLM_API_URL=http://host.docker.internal:8080/v1`

### 忘记登录密码

目前未提供密码找回功能，可通过数据库直接重置：

```bash
docker compose exec postgres psql -U fls_user -d family_learning
UPDATE users SET hashed_password = '$2b$12$...' WHERE username = 'your_username';
```

密码使用 bcrypt 加密，可借助 Python 生成新哈希：

```python
from passlib.context import CryptContext
pwd = CryptContext(schemes=["bcrypt"])
print(pwd.hash("new_password"))
```

---

## 更新日志

### v0.1.0 (2026-06-21)

- 初始化项目结构和 Docker Compose 编排
- 实现用户认证模块（注册/登录/JWT）
- 实现学习记录与艾宾浩斯复习计划
- 实现考试成绩追踪与趋势图
- 实现试卷 OCR 识别与错题自动收录
- 实现 AI 作答评估与解题生成
- 实现试卷整理（笔迹擦除/标注）
- 实现举一反三（LLM 相似题生成）
- 实现薄弱点分析与智能出卷
- 构建 10 个 Web 前端页面
- 集成 PaddleOCR 独立 Docker 服务
- 集成 ECharts 雷达图/趋势图

---

## 许可证

[MIT](./LICENSE)
