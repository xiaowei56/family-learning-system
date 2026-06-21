"""
API v1 路由

版本化 API，所有业务路由在此注册。
"""

from fastapi import APIRouter

router = APIRouter()

# ─── 认证模块 ──────────────────────────────────────
from app.api.v1.auth import router as auth_router
from app.api.v1.students import router as students_router
from app.api.v1.subjects import router as subjects_router
from app.api.v1.subjects import user_subjects_router

router.include_router(auth_router, prefix="/auth", tags=["认证"])
router.include_router(students_router, prefix="/students", tags=["学生档案"])
router.include_router(subjects_router, prefix="/subjects", tags=["科目配置"])
router.include_router(user_subjects_router, prefix="/users", tags=["用户科目"])

from app.api.v1.study_records import router as study_records_router
from app.api.v1.study_records import reviews_router
from app.api.v1.exam_results import router as exam_results_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.wrong_problems import router as wrong_problems_router
from app.api.v1.exam_papers import router as exam_papers_router
from app.api.v1.similar_problems import router as similar_problems_router
from app.api.v1.weak_points import router as weak_points_router

router.include_router(study_records_router, prefix="/study-records", tags=["学习记录"])
router.include_router(reviews_router, prefix="/reviews", tags=["复习管理"])
router.include_router(exam_results_router, prefix="/exam-results", tags=["考试成绩"])
router.include_router(dashboard_router, prefix="", tags=["仪表盘"])
router.include_router(wrong_problems_router, prefix="/wrong-problems", tags=["错题管理"])
router.include_router(exam_papers_router, prefix="/exam-papers", tags=["试卷整理"])
router.include_router(similar_problems_router, prefix="/similar-problems", tags=["举一反三"])
router.include_router(weak_points_router, prefix="", tags=["薄弱点分析"])
