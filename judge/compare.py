"""Output comparison utilities."""


def normalize_output(value):
    """Normalize harmless whitespace differences at line endings."""
    if value is None:
        return ""
    lines = str(value).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized = [line.rstrip() for line in lines]
    while normalized and normalized[-1] == "":
        normalized.pop()
    return "\n".join(normalized)


def outputs_match(actual, expected):
    """Return True when actual and expected outputs are equivalent."""
    return normalize_output(actual) == normalize_output(expected)
