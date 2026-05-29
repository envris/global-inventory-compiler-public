"""Validation utility functions."""

from ... import fields

# Cache identifier field names for quick access
IDENTIFIER_FIELDS = sorted(fields.get_identifier_field_names())
if "sid" in IDENTIFIER_FIELDS:
    IDENTIFIER_FIELDS.remove("sid")


def enforce_choice(value, variable_name: str, choices: list):
    """Shortcut function to raise custom ValueError"""
    if value not in choices:
        raise ValueError(f"{variable_name} {value} not in choices {choices}")


def enforce_type(value, variable_name: str, variable_type: type):
    """Shortcut function to raise custom Type error"""
    if not isinstance(value, variable_type):
        raise TypeError(f"{variable_name} {value} not of type {variable_type.__name__}")


def enforce_identifier_field(field_name: str):
    """Enforce that a field name is a valid identifier field."""
    enforce_choice(field_name, "Identifier field", IDENTIFIER_FIELDS)
