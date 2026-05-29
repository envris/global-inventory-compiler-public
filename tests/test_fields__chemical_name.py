"""Test cases for ChemicalNameField."""

from gic.fields import FieldTestCases
from gic.fields.chemical_name import ChemicalNameField

chemical_name_test_cases = FieldTestCases(
    valid=[
        "Acetone",
        "Benzene",
        "2-Propanol",
        "Sodium chloride",
        "Ethanol",
    ],
    invalid=[
        "=acetone",  # Starts with a dangerous character
        "Acetone\t",  # Contains a tab character
        "Benzene\r",  # Contains a newline character
        "word" * 600,  # Excessively long name
        "none",  # Non-specific placeholder
    ],
    valid_formatted=[],
    invalid_formatted=[],
    patched=[],
    generated=[],
)


def test_chemical_name_field():
    """Test ChemicalNameField with predefined test cases."""
    field = ChemicalNameField()
    field.test(chemical_name_test_cases)
