"""Collections of generic invalid values."""

# Generic null-meaning values that are not specific.
NULL_VALUES = {
    "none",
    "null",
    "-",
    "—",
    "_",
    "n/a",
}

# Non-specific names used as placeholders in some inventories
PLACEHOLDERS = {
    "[no public or meaningful name is available]",  # REACH
    "this cas rn has not been verified by cas and may be inaccurate.",  # JP-ISHA
    "confidential",
}

# CSV Injection attack risks
BAD_STARTS = ["=", "+", "-", "@"]
BAD_CHARS = ["\t", "\r"]
