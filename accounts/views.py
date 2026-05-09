"""Views for authentication and the dashboard."""

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
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

    context = {
        "total_problems": Problem.objects.filter(is_active=True).count(),
        "total_submissions": total_submissions,
        "accepted_count": accepted_count,
        "solved_count": solved_count,
        "accuracy": accuracy,
        "recent_submissions": submissions[:8],
    }
    return render(request, "accounts/dashboard.html", context)
