"""Python code executor."""

import os
import sys

from judge.cleanup import cleanup_directory
from judge.utils import (
    RunResult,
    VERDICT_ACCEPTED,
    VERDICT_RUNTIME_ERROR,
    VERDICT_TIME_LIMIT_EXCEEDED,
    create_temp_workspace,
    run_command,
)


def execute(code, stdin="", timeout=3):
    workspace = create_temp_workspace()
    try:
        source_path = workspace / "main.py"
        source_path.write_text(code, encoding="utf-8")
        python_cmd = os.getenv("PYTHON_EXECUTABLE") or sys.executable or "python"
        result = run_command([python_cmd, str(source_path)], stdin=stdin, cwd=workspace, timeout=timeout)

        if result.timed_out:
            return RunResult(False, VERDICT_TIME_LIMIT_EXCEEDED, result.stdout, result.stderr, result.execution_time)
        if result.returncode != 0:
            return RunResult(False, VERDICT_RUNTIME_ERROR, result.stdout, result.stderr, result.execution_time)
        return RunResult(True, VERDICT_ACCEPTED, result.stdout, result.stderr, result.execution_time)
    finally:
        cleanup_directory(workspace)
