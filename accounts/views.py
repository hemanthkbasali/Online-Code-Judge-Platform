"""Views for authentication and the dashboard."""

import json
from collections import defaultdict
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render

from accounts.forms import LoginForm, RegisterForm
from problems.models import Problem
from submissions.models import Submission


def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Welcome to CodeSentinel. Your account is ready.")
            return redirect("accounts:dashboard")
        messages.error(request, "Please fix the highlighted registration errors.")

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            auth_login(request, form.get_user())
            messages.success(request, "Login successful. Good to see you back.")
            return redirect("accounts:dashboard")
        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect("landing")


# ── Heatmap helpers ────────────────────────────────────────────────────────

def _level(count):
    """Map submission count → intensity level 0-4."""
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    return 4


def _build_heatmap_data(user):
    """
    Return heatmap grid + streak stats for the past 53 weeks (371 days).

    Grid: list of weeks (oldest → newest), each week is 7 day-dicts:
        {"date": "YYYY-MM-DD", "count": int, "level": 0-4}
    level == -1 means the cell is a future/invisible padding slot.
    Month labels: [{"label": "Jan", "col": week_index}, ...]
    """
    today = date.today()
    # Rewind to the most recent Sunday so the grid starts on a week boundary.
    # Python weekday(): Mon=0 … Sun=6 → days_since_sunday = (weekday+1)%7
    days_since_sunday = (today.weekday() + 1) % 7
    grid_start = today - timedelta(days=52 * 7 + days_since_sunday)
    grid_end = today

    # Single DB query: daily submission counts in the window
    qs = (
        Submission.objects.filter(
            user=user,
            created_at__date__gte=grid_start,
            created_at__date__lte=grid_end,
        )
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(cnt=Count("id"))
    )
    day_counts = {row["day"]: row["cnt"] for row in qs}

    # Build week grid ──────────────────────────────────────────────────────
    weeks = []
    week = []
    month_labels = []
    seen_months = set()
    col_idx = 0
    cursor = grid_start

    while cursor <= grid_end:
        cnt = day_counts.get(cursor, 0)
        week.append({"date": cursor.isoformat(), "count": cnt, "level": _level(cnt)})

        month_key = (cursor.year, cursor.month)
        if month_key not in seen_months:
            seen_months.add(month_key)
            month_labels.append({"label": cursor.strftime("%b"), "col": col_idx})

        if len(week) == 7:
            weeks.append(week)
            week = []
            col_idx += 1

        cursor += timedelta(days=1)

    if week:  # partial final week — pad so JS can treat the grid as rectangular
        while len(week) < 7:
            week.append({"date": "", "count": 0, "level": -1})
        weeks.append(week)

    # Streak computation ───────────────────────────────────────────────────
    active_dates = set(day_counts.keys())

    current_streak = 0
    check = today
    while check in active_dates:
        current_streak += 1
        check -= timedelta(days=1)

    longest_streak, run = 0, 0
    check = grid_start
    while check <= grid_end:
        if check in active_dates:
            run += 1
            longest_streak = max(longest_streak, run)
        else:
            run = 0
        check += timedelta(days=1)

    # This-month submissions ───────────────────────────────────────────────
    first_of_month = today.replace(day=1)
    month_submissions = Submission.objects.filter(
        user=user,
        created_at__date__gte=first_of_month,
    ).count()

    return {
        "weeks": weeks,
        "month_labels": month_labels,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_active_days": len(active_dates),
        "month_submissions": month_submissions,
    }


from contests.views import get_dashboard_contests

@login_required
def dashboard_view(request):
    submissions = Submission.objects.filter(user=request.user).select_related("problem")
    total_submissions = submissions.count()
    accepted_count = submissions.filter(verdict=Submission.VERDICT_ACCEPTED).count()
    solved_count = (
        submissions.filter(verdict=Submission.VERDICT_ACCEPTED)
        .values("problem_id")
        .distinct()
        .count()
    )
    accuracy = round((accepted_count / total_submissions) * 100, 1) if total_submissions else 0

    heatmap = _build_heatmap_data(request.user)
    upcoming_contests = get_dashboard_contests(limit=4)

    context = {
        "total_problems": Problem.objects.filter(is_active=True).count(),
        "total_submissions": total_submissions,
        "accepted_count": accepted_count,
        "solved_count": solved_count,
        "accuracy": accuracy,
        "recent_submissions": submissions[:10],
        # Heatmap — serialised for JS rendering
        "heatmap_json": json.dumps(heatmap["weeks"]),
        "heatmap_months_json": json.dumps(heatmap["month_labels"]),
        "current_streak": heatmap["current_streak"],
        "longest_streak": heatmap["longest_streak"],
        "total_active_days": heatmap["total_active_days"],
        "month_submissions": heatmap["month_submissions"],
        "upcoming_contests": upcoming_contests,
    }
    return render(request, "accounts/dashboard.html", context)
