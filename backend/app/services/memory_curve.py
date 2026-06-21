"""
艾宾浩斯遗忘曲线计算服务

基于艾宾浩斯遗忘曲线理论，计算复习时间间隔并查询到期复习项。
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.study_record import ReviewSchedule, StudyRecord

# ─── 基准复习间隔（单位：天）──────────────────────────
# 首次学习后第 1、2、4、7、15、30、90 天
_MEDIUM_INTERVALS = [1, 2, 4, 7, 15, 30, 90]


def calculate_review_dates(
    created_date: date,
    speed_mode: str = "medium",
) -> list[date]:
    """
    根据艾宾浩斯遗忘曲线计算所有复习日期。

    算法说明（基于艾宾浩斯遗忘曲线理论）：
        人类记忆在 20 分钟后遗忘 42%，1 小时后遗忘 56%，
        1 天后遗忘 74%，因此需要在特定时间点进行间隔复习。
        基准间隔为：1、2、4、7、15、30、90 天。

    Args:
        created_date: 学习记录的创建日期
        speed_mode: 复习速度模式
            - fast: 0.5x 间隔（四舍五入，最少 1 天）
            - medium: 1x 间隔（基准）
            - slow: 1.5x 间隔（四舍五入）

    Returns:
        按时间顺序排列的复习日期列表（已去重）
    """
    if speed_mode == "fast":
        factor = 0.5
    elif speed_mode == "slow":
        factor = 1.5
    else:
        factor = 1.0

    review_dates: list[date] = []
    for interval in _MEDIUM_INTERVALS:
        days = max(round(interval * factor), 1)
        review_dates.append(created_date + timedelta(days=days))

    # 去重（fast 模式下相邻间隔四舍五入后可能相同）
    unique_dates: list[date] = []
    for d in review_dates:
        if d not in unique_dates:
            unique_dates.append(d)

    return unique_dates


def get_due_reviews(
    user_id: str,
    review_date: date,
    db: Session,
) -> list[ReviewSchedule]:
    """
    获取指定用户在特定日期到期的所有待复习安排。

    到期规则：review_date <= 目标日期 且 status == 'pending'

    Args:
        user_id: 用户 UUID 字符串
        review_date: 目标日期（通常为今天）
        db: 数据库会话

    Returns:
        到期复习安排列表，按复习日期升序排列
    """
    return (
        db.query(ReviewSchedule)
        .join(StudyRecord)
        .filter(
            ReviewSchedule.status == "pending",
            ReviewSchedule.review_date <= review_date,
            StudyRecord.user_id == user_id,
        )
        .order_by(ReviewSchedule.review_date.asc())
        .all()
    )
