"""Seed presentation-ready demo problems."""

from django.core.management.base import BaseCommand

from problems.models import Problem, TestCase


class Command(BaseCommand):
    help = "Create demo problems and test cases for CodeSentinel."

    def handle(self, *args, **options):
        created = 0
        created += self._upsert_sum_problem()
        created += self._upsert_palindrome_problem()
        created += self._upsert_factorial_problem()
        self.stdout.write(self.style.SUCCESS(f"Demo data ready. Problems touched: {created}"))

    def _replace_cases(self, problem, cases):
        problem.test_cases.all().delete()
        for index, case in enumerate(cases, start=1):
            TestCase.objects.create(
                problem=problem,
                order=index,
                input_data=case["input"],
                expected_output=case["output"],
                is_hidden=case.get("hidden", True),
            )

    def _upsert_sum_problem(self):
        problem, _ = Problem.objects.update_or_create(
            title="Sum of Two Numbers",
            defaults={
                "statement": "Given two integers A and B, print their sum.",
                "input_format": "A single line containing two space-separated integers A and B.",
                "output_format": "Print one integer, the sum of A and B.",
                "constraints": "-10^9 <= A, B <= 10^9",
                "sample_input": "2 3",
                "sample_output": "5",
                "difficulty": Problem.DIFFICULTY_EASY,
                "time_limit": 2,
                "points": 100,
                "is_active": True,
            },
        )
        self._replace_cases(
            problem,
            [
                {"input": "2 3", "output": "5", "hidden": False},
                {"input": "-4 10", "output": "6"},
                {"input": "1000000000 1000000000", "output": "2000000000"},
            ],
        )
        return 1

    def _upsert_palindrome_problem(self):
        problem, _ = Problem.objects.update_or_create(
            title="Palindrome Check",
            defaults={
                "statement": "Given a string S, print YES if it is a palindrome, otherwise print NO.",
                "input_format": "A single string S.",
                "output_format": "Print YES or NO.",
                "constraints": "1 <= length of S <= 100000\nS contains lowercase English letters.",
                "sample_input": "level",
                "sample_output": "YES",
                "difficulty": Problem.DIFFICULTY_EASY,
                "time_limit": 2,
                "points": 120,
                "is_active": True,
            },
        )
        self._replace_cases(
            problem,
            [
                {"input": "level", "output": "YES", "hidden": False},
                {"input": "codesentinel", "output": "NO"},
                {"input": "abba", "output": "YES"},
            ],
        )
        return 1

    def _upsert_factorial_problem(self):
        problem, _ = Problem.objects.update_or_create(
            title="Factorial Modulo",
            defaults={
                "statement": "Given an integer N, print N! modulo 1000000007.",
                "input_format": "A single integer N.",
                "output_format": "Print N! modulo 1000000007.",
                "constraints": "0 <= N <= 100000",
                "sample_input": "5",
                "sample_output": "120",
                "difficulty": Problem.DIFFICULTY_MEDIUM,
                "time_limit": 2,
                "points": 180,
                "is_active": True,
            },
        )
        self._replace_cases(
            problem,
            [
                {"input": "5", "output": "120", "hidden": False},
                {"input": "0", "output": "1"},
                {"input": "10", "output": "3628800"},
                {"input": "100000", "output": "457992974"},
            ],
        )
        return 1
