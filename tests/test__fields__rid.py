"""Tests for the RIDField."""

from gic.fields import FieldTestCases
from gic.fields.rid import RIDField

rid_test_cases = FieldTestCases(
    valid=["RID1234567890ABCDEF", "RID0000000000000000", "RIDABCDEFGHIJKLMNOP"],
    invalid=[
        "RID1234567890ABCDE",
        "RID1234567890ABCDE12",
        "RID1234567890abcD",
        "RID1234567890ABcD",
        "RID1234567890ABc",
        "RID1234567890ABCD1",
        "1234567890ABCD",
        "RID1234567890ABCDEG2",
    ],
    valid_formatted=[],
    invalid_formatted=[],
    patched=[],
    generated=[],
)


def test_rid_field():
    """Test RIDField with predefined test cases."""
    field = RIDField()
    field.test(rid_test_cases)
