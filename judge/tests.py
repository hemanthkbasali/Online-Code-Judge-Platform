import subprocess
import sys
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase, override_settings

from judge.compare import normalize_output, outputs_match
from judge.service import evaluate_submission, run_single_case
from judge.utils import (
    VERDICT_ACCEPTED,
    VERDICT_RUNTIME_ERROR,
    VERDICT_TIME_LIMIT_EXCEEDED,
    VERDICT_WRONG_ANSWER,
    run_command,
)
from judge.validator import validate_code, validate_language


class NormalizeOutputTests(SimpleTestCase):
    def test_none_becomes_empty_string(self):
        self.assertEqual(normalize_output(None), "")

    def test_crlf_and_cr_are_converted_to_lf(self):
        self.assertEqual(normalize_output("a\r\nb\rc"), "a\nb\nc")

    def test_trailing_whitespace_is_stripped_per_line(self):
        self.assertEqual(normalize_output("a  \nb\t\n"), "a\nb")

    def test_trailing_blank_lines_are_removed(self):
        self.assertEqual(normalize_output("a\n\n\n"), "a")

    def test_leading_whitespace_is_preserved(self):
        self.assertEqual(normalize_output("  a\n b"), "  a\n b")

    def test_inner_blank_lines_are_preserved(self):
        self.assertEqual(normalize_output("a\n\nb"), "a\n\nb")


class OutputsMatchTests(SimpleTestCase):
    def test_equal_outputs_match(self):
        self.assertTrue(outputs_match("1 2 3\n", "1 2 3"))

    def test_line_ending_differences_match(self):
        self.assertTrue(outputs_match("a\r\nb\r\n", "a\nb\n"))

    def test_different_values_do_not_match(self):
        self.assertFalse(outputs_match("42", "43"))

    def test_internal_spacing_matters(self):
        self.assertFalse(outputs_match("1  2", "1 2"))

    def test_missing_line_does_not_match(self):
        self.assertFalse(outputs_match("a", "a\nb"))

    def test_none_matches_empty_expected_output(self):
        self.assertTrue(outputs_match(None, ""))


class ValidatorTests(SimpleTestCase):
    def test_language_is_normalised(self):
        self.assertEqual(validate_language("  Python "), (True, "python"))

    def test_unsupported_language_is_rejected(self):
        ok, message = validate_language("ruby")
        self.assertFalse(ok)
        self.assertIn("Unsupported", message)

    def test_missing_language_is_rejected(self):
        self.assertFalse(validate_language(None)[0])

    def test_blank_code_is_rejected(self):
        self.assertFalse(validate_code("   \n")[0])
        self.assertFalse(validate_code(None)[0])

    @override_settings(JUDGE_MAX_CODE_SIZE=10)
    def test_oversized_code_is_rejected(self):
        ok, message = validate_code("x" * 11)
        self.assertFalse(ok)
        self.assertIn("too large", message)

    @override_settings(JUDGE_MAX_CODE_SIZE=10)
    def test_size_limit_counts_bytes_not_characters(self):
        # Four characters, eight bytes in UTF-8; five of them exceed the limit.
        self.assertTrue(validate_code("é" * 4)[0])
        self.assertFalse(validate_code("é" * 6)[0])

    def test_valid_code_is_returned_unchanged(self):
        self.assertEqual(validate_code("print(1)"), (True, "print(1)"))


class RunCommandTests(SimpleTestCase):
    def test_missing_executable_is_reported(self):
        result = run_command(["definitely-not-a-real-binary-xyz"])
        self.assertEqual(result.returncode, 127)
        self.assertIn("not found", result.stderr)

    def test_timeout_returns_text_not_bytes(self):
        script = "import sys,time; print('partial'); sys.stdout.flush(); time.sleep(10)"
        result = run_command([sys.executable, "-c", script], timeout=1)
        self.assertTrue(result.timed_out)
        self.assertIsInstance(result.stdout, str)
        self.assertIsInstance(result.stderr, str)
        self.assertIn("partial", result.stdout)

    def test_timeout_bytes_output_is_decoded(self):
        # Some platforms/Python versions attach bytes to TimeoutExpired even with text=True.
        exc = subprocess.TimeoutExpired(
            ["x"], 1, output=b"partial \xff out", stderr=b"warn"
        )
        with mock.patch("judge.utils.subprocess.run", side_effect=exc):
            result = run_command(["x"], timeout=1)
        self.assertTrue(result.timed_out)
        self.assertEqual(result.stdout, "partial � out")
        self.assertEqual(result.stderr, "warn")

    def test_timeout_without_output_has_default_message(self):
        result = run_command([sys.executable, "-c", "import time; time.sleep(10)"], timeout=1)
        self.assertTrue(result.timed_out)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "Execution timed out.")


class PythonJudgeTests(SimpleTestCase):
    def test_program_output_is_captured(self):
        result = run_single_case("print(int(input()) * 2)", "python", stdin="21\n")
        self.assertTrue(result.ok)
        self.assertEqual(result.verdict, VERDICT_ACCEPTED)
        self.assertEqual(result.stdout.strip(), "42")

    def test_exception_is_a_runtime_error(self):
        result = run_single_case("raise ValueError('boom')", "python")
        self.assertFalse(result.ok)
        self.assertEqual(result.verdict, VERDICT_RUNTIME_ERROR)
        self.assertIn("ValueError", result.stderr)

    def test_infinite_loop_hits_time_limit(self):
        result = run_single_case("while True:\n    pass", "python", timeout=1)
        self.assertFalse(result.ok)
        self.assertEqual(result.verdict, VERDICT_TIME_LIMIT_EXCEEDED)

    def test_unsupported_language_fails_without_running(self):
        result = run_single_case("print(1)", "ruby")
        self.assertFalse(result.ok)
        self.assertEqual(result.verdict, VERDICT_RUNTIME_ERROR)

    def test_empty_code_fails_without_running(self):
        result = run_single_case("", "python")
        self.assertFalse(result.ok)
        self.assertIn("empty", result.stderr)


def _problem(cases, time_limit=2):
    """Build a stand-in for a Problem with a `test_cases.all()` manager."""
    test_cases = [
        SimpleNamespace(input_data=stdin, expected_output=expected)
        for stdin, expected in cases
    ]
    return SimpleNamespace(
        time_limit=time_limit,
        test_cases=SimpleNamespace(all=lambda: test_cases),
    )


class EvaluateSubmissionTests(SimpleTestCase):
    ADD_CODE = "a, b = map(int, input().split())\nprint(a + b)"

    def test_all_cases_pass(self):
        problem = _problem([("1 2\n", "3\n"), ("10 -4\n", "6")])
        result = evaluate_submission(problem, self.ADD_CODE, "python")
        self.assertEqual(result.verdict, VERDICT_ACCEPTED)
        self.assertIsNone(result.failed_test_number)

    def test_wrong_answer_reports_failing_case_number(self):
        problem = _problem([("1 2\n", "3"), ("2 2\n", "5")])
        result = evaluate_submission(problem, self.ADD_CODE, "python")
        self.assertEqual(result.verdict, VERDICT_WRONG_ANSWER)
        self.assertEqual(result.failed_test_number, 2)

    def test_runtime_error_stops_at_first_failing_case(self):
        problem = _problem([("x\n", "0"), ("1 2\n", "3")])
        result = evaluate_submission(problem, self.ADD_CODE, "python")
        self.assertEqual(result.verdict, VERDICT_RUNTIME_ERROR)
        self.assertEqual(result.failed_test_number, 1)

    def test_problem_without_test_cases_is_not_accepted(self):
        result = evaluate_submission(_problem([]), self.ADD_CODE, "python")
        self.assertEqual(result.verdict, VERDICT_WRONG_ANSWER)
        self.assertIn("No test cases", result.error_message)

    def test_invalid_language_is_rejected_before_running(self):
        result = evaluate_submission(_problem([("", "")]), "print(1)", "brainfuck")
        self.assertEqual(result.verdict, VERDICT_RUNTIME_ERROR)
        self.assertIn("Unsupported", result.error_message)
