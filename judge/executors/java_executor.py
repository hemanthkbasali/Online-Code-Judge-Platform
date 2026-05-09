"""Java code executor.

Java submissions must define `public class Main` because the judge writes the
source file as Main.java.
"""

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
        source_path = workspace / "Main.java"
        source_path.write_text(code, encoding="utf-8")

        compile_result = run_command(["javac", str(source_path)], cwd=workspace, timeout=max(timeout, 12))
        if compile_result.returncode != 0:
            return RunResult(
                False,
                VERDICT_COMPILATION_ERROR,
                compile_result.stdout,
                compile_result.stderr,
                compile_result.execution_time,
            )

        result = run_command(["java", "-cp", str(workspace), "Main"], stdin=stdin, cwd=workspace, timeout=timeout)
        if result.timed_out:
            return RunResult(False, VERDICT_TIME_LIMIT_EXCEEDED, result.stdout, result.stderr, result.execution_time)
        if result.returncode != 0:
            return RunResult(False, VERDICT_RUNTIME_ERROR, result.stdout, result.stderr, result.execution_time)
        return RunResult(True, VERDICT_ACCEPTED, result.stdout, result.stderr, result.execution_time)
    finally:
        cleanup_directory(workspace)
