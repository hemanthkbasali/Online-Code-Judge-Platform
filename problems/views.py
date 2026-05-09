"""Views for browsing and solving problems."""

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from problems.models import Problem
from submissions.models import Submission


STARTER_CODE = {
    "python": "import sys\n\n# Read input from stdin\n# Example: data = sys.stdin.read().strip()\n\ndef solve():\n    data = sys.stdin.read().strip()\n    print(data)\n\nif __name__ == \"__main__\":\n    solve()\n",
    "c": "#include <stdio.h>\n\nint main(void) {\n    // Write your solution here\n    return 0;\n}\n",
    "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n\n    // Write your solution here\n    return 0;\n}\n",
    "java": "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        // Write your solution here\n    }\n}\n",
}


def problem_list(request):
    query = request.GET.get("q", "").strip()
    difficulty = request.GET.get("difficulty", "").strip().lower()

    problems = Problem.objects.filter(is_active=True).annotate(total_cases=Count("test_cases"))
    if query:
        problems = problems.filter(Q(title__icontains=query) | Q(statement__icontains=query))
    if difficulty in {choice[0] for choice in Problem.DIFFICULTY_CHOICES}:
        problems = problems.filter(difficulty=difficulty)

    solved_problem_ids = set()
    if request.user.is_authenticated:
        solved_problem_ids = set(
            Submission.objects.filter(
                user=request.user,
                verdict=Submission.VERDICT_ACCEPTED,
            ).values_list("problem_id", flat=True)
        )

    context = {
        "problems": problems,
        "query": query,
        "selected_difficulty": difficulty,
        "difficulty_choices": Problem.DIFFICULTY_CHOICES,
        "solved_problem_ids": solved_problem_ids,
    }
    return render(request, "problems/list.html", context)


def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug, is_active=True)
    visible_cases = problem.test_cases.filter(is_hidden=False)
    user_submissions = []
    if request.user.is_authenticated:
        user_submissions = Submission.objects.filter(user=request.user, problem=problem)[:5]

    return render(
        request,
        "problems/detail.html",
        {
            "problem": problem,
            "visible_cases": visible_cases,
            "user_submissions": user_submissions,
        },
    )


@login_required
def code_editor(request, slug):
    problem = get_object_or_404(Problem, slug=slug, is_active=True)
    return render(
        request,
        "problems/editor.html",
        {
            "problem": problem,
            "starter_code": STARTER_CODE,
        },
    )
