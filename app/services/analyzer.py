from app.models import HabitLog
from datetime import date, timedelta

def calculate_weekly_score(habit):
    today = date.today()
    start_week = today - timedelta(days=7)

    logs = HabitLog.query.filter(
        HabitLog.habit_id == habit.id,
        HabitLog.log_date >= start_week,
        HabitLog.completed == True
    ).count()

    score = (logs / habit.target_per_week) * 100
    return round(score)

def get_status(score):

    if score >= 80:
        return "Excellent"
    elif score >= 50:
        return "Stable"
    else:
        return "Declining"
