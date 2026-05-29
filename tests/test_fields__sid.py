"""Test cases for SID field."""

from gic.fields import FieldTestCases
from gic.fields.sid import SIDField

sid_test_cases = FieldTestCases(
    valid=[1, 123456, 1001919, 100, 11, 222],
    invalid=[
        0,
        -1,
    ],
    valid_formatted=[],
    invalid_formatted=[],
    patched=[],
    generated=[],
)


def test_sid_field():
    """Test SIDField with predefined test cases."""
    field = SIDField()
    field.test(sid_test_cases)
