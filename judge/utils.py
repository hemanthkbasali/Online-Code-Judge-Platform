"""Shared judge helpers."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
import time

from django.conf import settings


VERDICT_ACCEPTED = "Accepted"
VERDICT_WRONG_ANSWER = "Wrong Answer"
VERDICT_COMPILATION_ERROR = "Compilation Error"
VERDICT_RUNTIME_ERROR = "Runtime Error"
VERDICT_TIME_LIMIT_EXCEEDED = "Time Limit Exceeded"


@dataclass
class RunResult:
    ok: bool
    verdict: str
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0
    message: str = ""


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    execution_time: float
    timed_out: bool = False


@dataclass
class JudgeResult:
    verdict: str
    execution_time: float = 0
    failed_test_number: int | None = None
    output: str = ""
    error_message: str = ""


def create_temp_workspace():
    base = Path(settings.JUDGE_TEMP_DIR)
    base.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="run_", dir=base))


def run_command(command, stdin="", cwd=None, timeout=None):
    """Run a subprocess safely using an argument list and a timeout."""
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            input=stdin,
            text=True,
            capture_output=True,
            cwd=str(cwd) if cwd else None,
            timeout=timeout or settings.JUDGE_DEFAULT_TIMEOUT,
            shell=False,
        )
        elapsed = round(time.perf_counter() - started, 4)
        return CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            execution_time=elapsed,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = round(time.perf_counter() - started, 4)
        return CommandResult(
            returncode=-1,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "Execution timed out.",
            execution_time=elapsed,
            timed_out=True,
        )
    except FileNotFoundError as exc:
        elapsed = round(time.perf_counter() - started, 4)
        return CommandResult(
            returncode=127,
            stdout="",
            stderr=f"Required compiler/interpreter not found: {exc.filename}",
            execution_time=elapsed,
        )
    except Exception as exc:
        elapsed = round(time.perf_counter() - started, 4)
        return CommandResult(
            returncode=1,
            stdout="",
            stderr=f"Judge process failed safely: {exc}",
            execution_time=elapsed,
        )
