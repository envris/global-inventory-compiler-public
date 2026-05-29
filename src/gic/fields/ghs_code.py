"""Definition of a GHS Code"""

from . import Field, ValidationError
from .utils.ghs_code_choices import is_recognised_ghs_code


class GHSCodeField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "ghs_code"
    dtype = str
    description = "Globally Harmonized System (GHS) Hazard Code"
    is_identifier = False
    derived_from = None

    @staticmethod
    def validate(value: str) -> bool:
        if not is_recognised_ghs_code(value):
            raise ValidationError("Unrecognised GHS code")
        return True

    @staticmethod
    def has_format(value: str) -> bool:
        raise NotImplementedError("has_format method not defined for this field")

    @staticmethod
    def patch(value):
        raise NotImplementedError("patch method not defined for this field")

    @staticmethod
    def generate(required_value):
        raise NotImplementedError("generate method not defined for GHS Code field")
