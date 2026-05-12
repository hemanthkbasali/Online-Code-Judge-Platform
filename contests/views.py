"""Views for the contests app."""

from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from contests.models import Contest


def _split_contests(qs):
    """Partition a queryset into live, upcoming, and completed lists."""
    live, upcoming, completed = [], [], []
    for c in qs:
        s = c.status
        if s == "live":
            live.append(c)
        elif s == "upcoming":
            upcoming.append(c)
        else:
            completed.append(c)
    return live, upcoming, completed


def contest_list(request):
    """Public contest listing page."""
    contests = Contest.objects.filter(is_active=True).order_by("start_time")
    live, upcoming, completed = _split_contests(contests)

    return render(request, "contests/list.html", {
        "live_contests": live,
        "upcoming_contests": upcoming,
        "completed_contests": completed,
        "total": contests.count(),
    })


def contest_detail(request, slug):
    """Detail / registration page for a single contest."""
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    return render(request, "contests/detail.html", {"contest": contest})


# ── Dashboard widget helper ─────────────────────────────────────────────────

def get_dashboard_contests(limit=4):
    """
    Return a short list of contests for the dashboard widget:
    live contests first, then upcoming, capped at `limit`.
    """
    now = timezone.now()
    contests = (
        Contest.objects
        .filter(is_active=True, start_time__gte=now - __import__('datetime').timedelta(days=1))
        .order_by("start_time")[:limit + 4]
    )
    live, upcoming, _ = _split_contests(contests)
    combined = live + upcoming
    return combined[:limit]
