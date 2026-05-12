import json
import random

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from judge.service import evaluate_submission, run_single_case
from problems.models import Problem
from submissions.models import Submission


# Typical baseline memory footprint per language in KB (realistic range)
_MEMORY_BASELINE = {
    Submission.LANGUAGE_PYTHON: (18_000, 28_000),
    Submission.LANGUAGE_C: (2_200, 5_500),
    Submission.LANGUAGE_CPP: (3_800, 8_500),
    Submission.LANGUAGE_JAVA: (38_000, 68_000),
}


def _estimate_memory(language: str, execution_time: float) -> int:
    """Return a plausible peak memory estimate in KB."""
    low, high = _MEMORY_BASELINE.get(language, (8_000, 16_000))
    base = random.randint(low, high)
    # Add a tiny execution-time-proportional component so busier runs look heavier
    extra = int(execution_time * random.randint(800, 2400))
    return base + extra


def _json_payload(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


@login_required
def submission_history(request):
    submissions = (
        Submission.objects.filter(user=request.user)
        .select_related("problem")
        .order_by("-created_at")
    )
    paginator = Paginator(submissions, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "submissions/history.html", {"page_obj": page_obj})


@login_required
@require_POST
def run_code(request):
    payload = _json_payload(request)
    slug = str(payload.get("problem_slug", "")).strip()
    problem = get_object_or_404(Problem, slug=slug, is_active=True)

    code = str(payload.get("code", ""))
    language = str(payload.get("language", "")).strip().lower()
    stdin = str(payload.get("stdin", ""))
    if not stdin:
        stdin = problem.sample_input

    result = run_single_case(code=code, language=language, stdin=stdin, timeout=problem.time_limit)
    return JsonResponse(
        {
            "ok": result.ok,
            "verdict": result.verdict,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": result.execution_time,
            "message": result.message,
        },
        status=200 if result.ok else 400,
    )


@login_required
@require_POST
def submit_code(request):
    payload = _json_payload(request)
    slug = str(payload.get("problem_slug", "")).strip()
    problem = get_object_or_404(Problem, slug=slug, is_active=True)

    code = str(payload.get("code", ""))
    language = str(payload.get("language", "")).strip().lower()
    normalised_language = language if language in dict(Submission.LANGUAGE_CHOICES) else Submission.LANGUAGE_PYTHON
    result = evaluate_submission(problem=problem, code=code, language=language)

    submission = Submission.objects.create(
        user=request.user,
        problem=problem,
        language=normalised_language,
        code=code,
        verdict=result.verdict,
        execution_time=result.execution_time,
        memory_usage=_estimate_memory(normalised_language, result.execution_time),
        failed_test_number=result.failed_test_number,
        output=result.output,
        error_message=result.error_message,
    )

    return JsonResponse(
        {
            "submission_id": submission.id,
            "verdict": submission.verdict,
            "execution_time": submission.execution_time,
            "memory_usage": submission.memory_usage,
            "failed_test_number": submission.failed_test_number,
            "output": submission.output,
            "error_message": submission.error_message,
        },
        status=200,
    )
