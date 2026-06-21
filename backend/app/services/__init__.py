"""
业务服务层

封装各业务模块的核心逻辑，供 API 路由调用。
后续各 Service 在此处注册：

- StudyRecordService    — 学习记录管理
- ReviewService         — 艾宾浩斯复习计划
- ExamResultService     — 考试成绩追踪
- WrongProblemService   — 错题管理 & OCR 识别
- ExamPaperService      — 试卷整理 & 去笔迹
- SimilarProblemService — 举一反三
- WeakPointService      — 薄弱点分析
- PracticePaperService  — 智能组卷
- LearningAdviceService — 学习建议
- LLMService            — LLM API 调用封装
- OCRService            — PaddleOCR 调用封装
- MinIOService          — MinIO 对象存储封装
"""
