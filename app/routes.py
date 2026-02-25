from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify,abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta
from app.models import User, Habit, HabitLog
from app import db
from app.services.analyzer import calculate_weekly_score, get_status
from app.utils import generate_insight, generate_tip

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("register.html")

@main.route("/register", methods=["GET", "POST"])
def register(): 
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed = generate_password_hash(password)

        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()

        flash("Compte créé")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Identifiants incorrects")

    return render_template("login.html")

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@main.route("/dashboard")
@login_required
def dashboard():

    habits = Habit.query.filter_by(user_id=current_user.id).all()

    habit_data = []

    for habit in habits:
        score = calculate_weekly_score(habit)
        score = max(0, min(score, 100))

        status = get_status(score)
        insight = generate_insight(habit.name, status)
        tip = generate_tip(status, habit.target_per_week)

        # determine whether the habit is completed today
        today_log = HabitLog.query.filter_by(habit_id=habit.id, log_date=date.today()).first()
        is_completed_today = True if today_log and today_log.completed else False

        habit_data.append({
            "id": habit.id,
            "name": habit.name,
            "score": score,
            "status": status,
            "completed": round((score/100) * habit.target_per_week),
            "target": habit.target_per_week,
            "insight": insight,
            "tip": tip,
            "is_completed_today": is_completed_today
        })

        today = date.today()

        for h in habit_data:
            log = HabitLog.query.filter_by(
                habit_id=h["id"],
                log_date=today
            ).first()

            h["is_completed_today"] = True if log and log.completed else False

    return render_template("dashboard.html", habits=habit_data)


@main.route("/habits", methods=["GET", "POST"])
@login_required
def habits():
    if request.method == "POST":
        name = request.form["name"]
        target = request.form["target"]

        habit = Habit(
            name=name,
            target_per_week=target,
            user_id=current_user.id
        )

        db.session.add(habit)
        db.session.commit()

        return redirect(url_for("main.dashboard"))

    user_habits = Habit.query.filter_by(user_id=current_user.id).all()
    for habit in user_habits:
        log = HabitLog.query.filter_by(
            habit_id=habit.id,
            log_date=date.today()
        ).first()

        habit.is_completed_today = True if log and log.completed else False
    return render_template("dashboard.html", habits=user_habits)

@main.route("/delete_habit/<int:habit_id>", methods=["POST"])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        abort(403)

    db.session.delete(habit)
    db.session.commit()

    return redirect(url_for("main.habits"))


@main.route("/toggle/<int:habit_id>")
@login_required
def toggle_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    if habit.user_id != current_user.id:
        abort(403)

    today = date.today()

    log = HabitLog.query.filter_by(
        habit_id=habit_id,
        log_date=today
    ).first()

    if log:
        log.completed = not log.completed
    else:
        log = HabitLog(
            habit_id=habit_id,
            completed=True
        )
        db.session.add(log)

    db.session.commit()
    return redirect(url_for("main.dashboard"))

@main.route("/api/weekly-data")
@login_required
def weekly_data():

    today = date.today()
    start = today - timedelta(days=6)

    habits = Habit.query.filter_by(user_id=current_user.id).all()

    labels = []
    for i in range(7):
        day = start + timedelta(days=i)
        labels.append(day.strftime("%a"))

    datasets = []

    for habit in habits:
        data = []

        for i in range(7):
            day = start + timedelta(days=i)

            log = HabitLog.query.filter_by(
                habit_id=habit.id,
                log_date=day
            ).first()

            data.append(1 if log and log.completed else 0)

        datasets.append({
            "label": habit.name,
            "data": data,
            "fill": False,
            "tension": 0.3
        })

    return jsonify({
        "labels": labels,
        "datasets": datasets
    })
