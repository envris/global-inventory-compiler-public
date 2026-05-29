"""Test cases for ListTagField."""

from gic.fields import FieldTestCases
from gic.fields.list_tag import ListTagField

list_tag_test_cases = FieldTestCases(
    valid=["AU-AIIC", "EU-REACH_R", "AU-IChEMS", "Short list name"],
    invalid=["sh", "This list tag is way too long to be valid"],
    valid_formatted=[],
    invalid_formatted=[],
    patched=[],
    generated=[],
)


def test_list_tag_field():
    """Test the ListTagField with predefined test cases."""
    field = ListTagField()
    field.test(list_tag_test_cases)
