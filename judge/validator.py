"""Input validation for judge requests."""

from django.conf import settings


SUPPORTED_LANGUAGES = {"python", "c", "cpp", "java"}


def validate_language(language):
    language = (language or "").strip().lower()
    if language not in SUPPORTED_LANGUAGES:
        return False, "Unsupported language selected."
    return True, language


def validate_code(code):
    if code is None or not str(code).strip():
        return False, "Code cannot be empty."
    if len(str(code).encode("utf-8")) > settings.JUDGE_MAX_CODE_SIZE:
        return False, "Code is too large for this judge."
    return True, str(code)
