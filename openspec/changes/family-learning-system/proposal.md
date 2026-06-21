## Why

家庭学习场景中，学生需要统一管理学习记录、错题、考试成绩，并借助 AI 能力进行智能复习、错题分析和针对性练习。目前缺乏一套面向 K12 阶段、部署在家庭 NAS、支持多端使用的整合系统。本项目旨在打造一个**纯内网、本地 AI、数据私有的家庭学习辅助平台**。

## What Changes

- 新建一套家庭学习系统，包含 Web 端和 Android 端
- 后端基于 Python FastAPI，部署在家庭 NAS（Docker Compose）
- 前端使用响应式 Web（React/Vue3） + Flutter（Android）
- AI 能力依赖本地部署的 PaddleOCR 和内网 LLM API
- 数据存储使用 PostgreSQL + MinIO
- 系统分为三个阶段交付：P1 基础功能 → P2 AI 接入 → P3 智能闭环

## Capabilities

### New Capabilities

- `study-records`: 学习记录与艾宾浩斯记忆曲线复习提醒。按科目分类管理，支持富文本笔记、自动计算复习时间点、手动标记已掌握
- `exam-tracking`: 考试成绩追踪与得分率趋势分析。支持日常练习/周测/月考/期中/期末五种类型，按科目生成独立曲线并提供多科对比
- `exam-paper-ocr`: 试卷与错题拍照识别。PaddleOCR 识别题目，LLM 判断正误、生成解题步骤和图示解析（SVG/Chart.js/MathJax/流程图）
- `paper-management`: 试卷整理与归档。拍照存档、去笔迹重印、在线批注复习
- `similar-problems`: 基于错题的举一反三。同知识点同类题生成，附带解题思路总结
- `weak-point-analysis`: 薄弱点分析与智能出卷。综合错题+成绩数据识别薄弱点，AI 组卷，生成学习诊断报告（学习建议/学习方法/记忆方法）
- `user-auth`: 用户管理。支持多学生/家长账号，年级切换（小/初/高）
- `dashboard`: 首页概览。今日复习提醒、最近错题、成绩概览

### Modified Capabilities

- 无（新项目，无现有 spec）

## Impact

- 新建 Docker Compose 部署项目（Nginx + FastAPI + PostgreSQL + MinIO + Redis）
- 新建 Python FastAPI 后端服务
- 新建 Web 前端（React/Vue3）项目
- 新建 Flutter Android App 项目
- 依赖：PaddleOCR（本地部署）、内网 LLM API（192.168.110.7/v1）
