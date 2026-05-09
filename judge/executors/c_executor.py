"""C code executor."""

import os

from judge.cleanup import cleanup_directory
from judge.utils import (
    RunResult,
    VERDICT_ACCEPTED,
    VERDICT_COMPILATION_ERROR,
    VERDICT_RUNTIME_ERROR,
    VERDICT_TIME_LIMIT_EXCEEDED,
    create_temp_workspace,
    run_command,
)


def execute(code, stdin="", timeout=3):
    workspace = create_temp_workspace()
    try:
        source_path = workspace / "main.c"
        executable = workspace / ("main.exe" if os.name == "nt" else "main")
        source_path.write_text(code, encoding="utf-8")

        compile_result = run_command(
            ["gcc", str(source_path), "-O2", "-std=c11", "-o", str(executable)],
            cwd=workspace,
            timeout=max(timeout, 12),
        )
        if compile_result.returncode != 0:
            return RunResult(
                False,
                VERDICT_COMPILATION_ERROR,
                compile_result.stdout,
                compile_result.stderr,
                compile_result.execution_time,
            )

        result = run_command([str(executable)], stdin=stdin, cwd=workspace, timeout=timeout)
        if result.timed_out:
            return RunResult(False, VERDICT_TIME_LIMIT_EXCEEDED, result.stdout, result.stderr, result.execution_time)
        if result.returncode != 0:
            return RunResult(False, VERDICT_RUNTIME_ERROR, result.stdout, result.stderr, result.execution_time)
        return RunResult(True, VERDICT_ACCEPTED, result.stdout, result.stderr, result.execution_time)
    finally:
        cleanup_directory(workspace)
