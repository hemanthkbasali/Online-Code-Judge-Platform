"""High-level judge service used by views."""

from judge.compare import outputs_match
from judge.executors import c_executor, cpp_executor, java_executor, python_executor
from judge.utils import (
    JudgeResult,
    VERDICT_ACCEPTED,
    VERDICT_RUNTIME_ERROR,
    VERDICT_WRONG_ANSWER,
)
from judge.validator import validate_code, validate_language


EXECUTORS = {
    "python": python_executor.execute,
    "c": c_executor.execute,
    "cpp": cpp_executor.execute,
    "java": java_executor.execute,
}


def run_single_case(code, language, stdin="", timeout=3):
    valid_language, language_or_error = validate_language(language)
    if not valid_language:
        return _failed_run(language_or_error)

    valid_code, code_or_error = validate_code(code)
    if not valid_code:
        return _failed_run(code_or_error)

    try:
        executor = EXECUTORS[language_or_error]
        return executor(code_or_error, stdin=stdin, timeout=timeout)
    except Exception as exc:
        return _failed_run(f"Judge failed safely: {exc}", verdict=VERDICT_RUNTIME_ERROR)


def evaluate_submission(problem, code, language):
    valid_language, language_or_error = validate_language(language)
    if not valid_language:
        return JudgeResult(verdict=VERDICT_RUNTIME_ERROR, error_message=language_or_error)

    valid_code, code_or_error = validate_code(code)
    if not valid_code:
        return JudgeResult(verdict=VERDICT_RUNTIME_ERROR, error_message=code_or_error)

    test_cases = list(problem.test_cases.all())
    if not test_cases:
        return JudgeResult(
            verdict=VERDICT_WRONG_ANSWER,
            error_message="No test cases are configured for this problem.",
        )

    total_time = 0.0
    for index, test_case in enumerate(test_cases, start=1):
        run_result = run_single_case(
            code=code_or_error,
            language=language_or_error,
            stdin=test_case.input_data,
            timeout=problem.time_limit,
        )
        total_time += run_result.execution_time

        if not run_result.ok:
            return JudgeResult(
                verdict=run_result.verdict,
                execution_time=round(total_time, 4),
                failed_test_number=index,
                output=run_result.stdout,
                error_message=run_result.stderr or run_result.message,
            )

        if not outputs_match(run_result.stdout, test_case.expected_output):
            return JudgeResult(
                verdict=VERDICT_WRONG_ANSWER,
                execution_time=round(total_time, 4),
                failed_test_number=index,
                output=run_result.stdout,
                error_message="Output did not match the expected answer.",
            )

    return JudgeResult(verdict=VERDICT_ACCEPTED, execution_time=round(total_time, 4), output="All test cases passed.")


def _failed_run(message, verdict=VERDICT_RUNTIME_ERROR):
    from judge.utils import RunResult

    return RunResult(False, verdict, stdout="", stderr=message, execution_time=0, message=message)
