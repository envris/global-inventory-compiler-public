"""Test cases for ECNumberField."""

from gic.fields import FieldTestCases
from gic.fields.ec_number import ECNumberField

ec_number_test_cases = FieldTestCases(
    valid=[
        "260-246-1",  # Checkdigit = 1
        "424-870-1",  # Checkdigit = 10
        "200-002-3",
        "200-067-8",
        "226-764-7",
        "611-422-5",
        "260-343-9",
        "260-289-6",
        "260-281-2",
        "260-277-0",
        # Tests for new alphanumeric format
        "A00-001-5",
    ],
    invalid=[
        "123456-7-8",
        "123-4-5",
        "123-45-67",
        "123-45-A",
        "123-45-6",
        "260-246-2",
        "000-000-0",
        "123-456-7",
        "123-45-6",
    ],
    valid_formatted=["260-246-1", "424-870-1", "200-002-3", "200-067-8", "226-764-7"],
    invalid_formatted=[
        "123456-7-",
        "123-4-5",
        "123-45-67",
        "123-45-A",
        "1234567",
        "12345-6",
    ],
    patched=[
        ("2602461", "260-246-1"),
        ("4248701", "424-870-1"),
        (2602461, "260-246-1"),
        (4248701, "424-870-1"),
    ],
    generated=[],
)


def test_ec_number_field():
    """Test ECNumberField with predefined test cases."""
    field = ECNumberField()
    field.test(ec_number_test_cases)
