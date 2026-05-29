"""Test cases for GHSCodeField."""

from gic.fields import FieldTestCases
from gic.fields.ghs_code import GHSCodeField

ghs_code_test_cases = FieldTestCases(
    valid=["H200", "H201", "H202", "H203"],
    invalid=["H999", "X200", "H20A", "H20"],
    valid_formatted=[],
    invalid_formatted=[],
    patched=[],
    generated=[],
)


def test_ghs_code_field():
    """Test GHSCodeField with predefined test cases."""
    field = GHSCodeField()
    field.test(ghs_code_test_cases)
