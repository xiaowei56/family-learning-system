## Context

家庭学习系统为 K12 学生提供私有化部署的学习辅助平台，运行于家庭 NAS 内网环境。系统需要覆盖学习记录、错题管理、成绩追踪、试卷整理、AI 解题、举一反三、薄弱点分析和智能出卷等完整学习闭环。

**约束条件：**
- 纯内网部署，不连接公网，无需加密
- AI 能力依赖本地 PaddleOCR（CPU）和内网 LLM API（192.168.110.7/v1）
- Docker Compose 部署，NAS 资源有限（需考虑 CPU 和内存优化）
- Web + Android 双端覆盖

## Goals / Non-Goals

**Goals:**
- 建立可扩展的后端架构（FastAPI），支持 6 大业务模块
- 实现 PaddleOCR 本地 CPU 推理服务，延迟可接受
- 对接内网 LLM API，统一 AI 服务调用层
- 数据模型覆盖所有核心实体，支持分阶段交付
- Web 端响应式布局覆盖桌面和手机浏览器
- Flutter Android App 与 Web 端共享 API

**Non-Goals:**
- 不接入公网 AI 服务（如 OpenAI、通义千问等）
- 不做高并发/高可用设计（家庭场景，单机使用）
- 不做 iOS App（初期只覆盖 Android）
- 不做实时音视频或直播功能
- 不涉及教育内容版权管理

## Decisions

### 1. 后端框架：Python FastAPI
- **原因：** Python 生态对 AI/OCR/LLM 支持最好，FastAPI 异步性能优异，自动生成 OpenAPI 文档便于前端对接
- **替代方案：** Node.js NestJS（AI 生态不如 Python）、Java Spring Boot（太重，NAS 资源有限）

### 2. Web 前端：Vue3 + Element Plus
- **原因：** Vue3 生态成熟，Element Plus 表单/表格/图表组件丰富，适合管理后台类型应用
- **替代方案：** React + Ant Design（同样优秀，但团队偏好 Vue）

### 3. Android：Flutter
- **原因：** 未来可复用至 iOS，单代码库维护，Material Design 原生体验
- **替代方案：** 原生 Kotlin（需要单独维护 iOS）

### 4. AI 服务层独立封装
- 所有 AI 调用（OCR + LLM）通过统一的 `ai_service` 模块访问
- OCR 和 LLM 各自封装为独立 Service，便于替换实现
- LLM API 兼容 OpenAI 格式，调用 `http://192.168.110.7/v1`

### 5. 图片存储：MinIO
- **原因：** 兼容 S3 API，轻量级，与 PostgreSQL 分离存储，避免数据库 BLOB
- **替代方案：** 本地文件系统（不利于扩展）

### 6. 分阶段交付
- P1：无 AI 依赖的基础 CRUD 功能，快速可用
- P2：接入 AI 能力，核心亮点功能
- P3：智能学习闭环，完整系统

## Risks / Trade-offs

- **Risk: CPU 上 PaddleOCR 推理慢** → 限制图片大小（压缩至 1080p），异步任务队列处理
- **Risk: 本地 LLM 解题质量不稳定** → 设计人工纠错机制，用户可反馈错误
- **Risk: NAS 资源不足同时跑 PostgreSQL + MinIO + OCR + LLM** → 建议分离部署，LLM 可跑在其他机器
- **Risk: 去笔迹重印效果可能不完美** → 提供手动裁剪/修复工具，允许用户调整
- **Trade-off: 纯内网无公网访问** → 安全性提高，但 Web 端无法在家庭外使用（Android 可通过 VPN 或 Tailscale 回家庭网络）
