"""Temporary file cleanup helpers."""

import shutil
from pathlib import Path


def cleanup_directory(path):
    """Remove a temporary judge directory without crashing the request."""
    if not path:
        return
    try:
        target = Path(path)
        if target.exists() and target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
    except Exception:
        # Cleanup must never hide the real judge result from the user.
        pass
