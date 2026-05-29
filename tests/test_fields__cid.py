"""Test cases for CIDField."""

from gic.fields import FieldTestCases
from gic.fields.cid import CIDField

cid_test_cases = FieldTestCases(
    valid=[
        "CID123456",
        "CID1",
        "CID9876543210",
    ],
    invalid=[
        "123456",
        "CID 123456",
        "CID ABCDEF",
        "CID -12345",
    ],
    valid_formatted=[
        "CID123456",
        "CID1",
        "CID9876543210",
    ],
    invalid_formatted=[
        "123456",
        "CID 123456",
        "CID ABCDEF",
        "CID -12345",
    ],
    patched=[
        (123456, "CID123456"),
        ("CID7890", "CID7890"),
        ("456789", "CID456789"),
    ],
    generated=[],
)


def test_cid_field():
    """Test CIDField with predefined test cases."""
    field = CIDField()
    field.test(cid_test_cases)
