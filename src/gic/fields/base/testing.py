"""Classes and functions for testing field definitions."""

from dataclasses import dataclass, field


@dataclass
class FieldTestCases:
    """Base class for field test cases."""

    valid: list[str | int | float] = field(default_factory=list)
    invalid: list[str | int | float] = field(default_factory=list)
    valid_formatted: list[str] = field(default_factory=list)
    invalid_formatted: list[str] = field(default_factory=list)
    patched: list[tuple] = field(default_factory=list)  # (input, expected_output)
    generated: list[tuple] = field(
        default_factory=list
    )  # (required_value, expected_output)
