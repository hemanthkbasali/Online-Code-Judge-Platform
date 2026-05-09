"""Small project-level views."""

from django.shortcuts import render

from problems.models import Problem
from submissions.models import Submission


def landing_page(request):
    """Premium public landing page with live platform stats."""
    total_problems = Problem.objects.filter(is_active=True).count()
    total_submissions = Submission.objects.count()
    accepted_submissions = Submission.objects.filter(verdict=Submission.VERDICT_ACCEPTED).count()
    accuracy = round((accepted_submissions / total_submissions) * 100, 1) if total_submissions else 0

    context = {
        "total_problems": total_problems,
        "total_submissions": total_submissions,
        "accepted_submissions": accepted_submissions,
        "accuracy": accuracy,
    }
    return render(request, "landing.html", context)
