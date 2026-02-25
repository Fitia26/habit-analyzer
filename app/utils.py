def generate_insight(habit_name, status):

    if status == "Excellent":
        return f"Great job on {habit_name}! Keep up the momentum."

    elif status == "Stable":
        return f"{habit_name} is stable. Try pushing a little further."

    else:
        return f"Your {habit_name} habit is declining. Consider lowering the goal or improving consistency."


def generate_tip(status, target):

    if status == "Declining":
        return "Try lowering your weekly goal or attach this habit to an existing routine."

    elif status == "Stable":
        return "Try setting a reminder or fixing a specific time of day."

    else:
        return "Great consistency. Consider increasing your challenge slightly."
