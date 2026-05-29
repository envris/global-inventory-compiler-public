"""Base level class a field."""

import logging

from .exceptions import ValidationError
from .testing import FieldTestCases


class Field:
    """
    Base level class for a field.

    Attributes:
        name (str): The name of the field used through the code.
        dtype (type): The expected data type.
        description (str): Long name or short description of the field.
        is_identifier (bool): True if the field is a chemical identifier.
            These fields may be used in the Inventory.
        derived_from (str | None): Name of the field this field is
            derived from, or None if not derived from another field.
    """

    name: str
    dtype: type
    description: str
    is_identifier: bool
    is_substance_identifier: bool
    derived_from: str | None

    @staticmethod
    def validate(value) -> bool:
        """
        Returns True if valid or raised ValidationError value is invalid.
        Values are assumed to be of correct data type.
        """
        raise NotImplementedError("validate method not defined for this field")

    @staticmethod
    def has_format(value: str) -> bool:
        """
        Returns True if value has correct pattern or format, but is not
        necessarily valid. This method is typically implemented when extracting
        values from unstructured data sources using regular expressions.
        """
        raise NotImplementedError("has_format method not defined for this field")

    @staticmethod
    def patch(value):
        """
        Return value after correcting expected faults, or same value if no
        correction is made.
        """
        raise NotImplementedError("patch method not defined for this field")

    @staticmethod
    def generate(required_value):
        """Generate a value from another field's value"""
        raise NotImplementedError("generate method not defined for this field")

    def test(self, test_cases: FieldTestCases) -> bool:
        """Run test cases for this field definition"""
        # Assert valid values are valid
        for value in test_cases.valid:
            logging.debug(f"Testing valid value: {value}")
            if self.validate(value) is not True:
                raise AssertionError(f"Valid value {value} failed validation")
        # Assert invalid values are invalid
        for value in test_cases.invalid:
            logging.debug(f"Testing invalid value: {value}")
            try:
                self.validate(value)
            except ValidationError:
                pass
            else:
                raise AssertionError(f"Invalid value {value} passed validation")
        # Assert formatted values are correctly identified
        for value in test_cases.valid_formatted:
            logging.debug(f"Testing valid_formatted value: {value}")
            if self.has_format(value) is not True:
                raise AssertionError(
                    f"Valid formatted value {value} failed format check"
                )
        for value in test_cases.invalid_formatted:
            logging.debug(f"Testing invalid_formatted value: {value}")
            if self.has_format(value) is not False:
                raise AssertionError(
                    f"Invalid formatted value {value} passed format check"
                )
        # Assert patched values are correctly transformed
        for input_value, expected_output in test_cases.patched:
            logging.debug(
                f"Testing patch: input={input_value}, expected={expected_output}"
            )
            if self.patch(input_value) != expected_output:
                patch_output = self.patch(input_value)
                try:
                    patch_output = self.serialise(patch_output)
                except NotImplementedError:
                    pass
                if patch_output != expected_output:
                    raise AssertionError(
                        f"Patch output {patch_output} does not match "
                        f"expected {expected_output}"
                    )
        for required_value, expected_output in test_cases.generated:
            test_output = self.generate(required_value)
            try:
                test_output = self.serialise(test_output)
            except NotImplementedError:
                pass
            logging.debug(
                f"Testing generate: required={required_value}, expected={test_output}"
            )
            if test_output != expected_output:
                raise AssertionError(
                    f"Generated value {test_output} does not match "
                    f"expected {expected_output}"
                )
        return True

    @staticmethod
    def serialise(generated) -> str:
        """Serialise field value for storage or comparison."""
        raise NotImplementedError("serialise method not defined for this field")

    @staticmethod
    def sort_values(values: list) -> list:
        """Optional method to custom sort a list of values for consistent ordering."""
        return sorted(values)
