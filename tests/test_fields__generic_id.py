"""Test cases for GenericID fields."""

from gic.fields import generic_id

from .test_fields__chemical_name import chemical_name_test_cases


def test_generic_id_fields():
    """Test all GenericID fields with the same test cases to ensure they have the same
    validation logic."""
    for i in range(1, 6):
        field_class = getattr(generic_id, f"GenericID{i}Field")
        field = field_class()
        field.test(chemical_name_test_cases)
