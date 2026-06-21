"""
数据模型包

SQLAlchemy ORM 模型定义，对应需求规格说明书中的核心实体。

导入 Base 以供 Alembic / init_db 发现所有模型。
"""

from app.core.database import Base

from app.models.user import User
from app.models.student import Student
from app.models.subject import Subject, UserSubject
from app.models.study_record import StudyRecord, ReviewSchedule
from app.models.exam_result import ExamResult
from app.models.wrong_problem import WrongProblem
from app.models.exam_paper import ExamPaper, PaperAnnotation
from app.models.advanced_analysis import SimilarProblem, WeakPoint, PracticePaper, LearningAdvice

__all__ = [
    "Base",
    "User",
    "Student",
    "Subject",
    "UserSubject",
    "StudyRecord",
    "ReviewSchedule",
    "ExamResult",
    "WrongProblem",
    "ExamPaper",
    "PaperAnnotation",
    "SimilarProblem",
    "WeakPoint",
    "PracticePaper",
    "LearningAdvice",
]
