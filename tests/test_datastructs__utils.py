"""Test selected utility functions"""

from gic import fields
from gic.datastructs.utils.collection import redact_identifier


def test_redact_identifiers():
    """Test redacting identifiers."""
    identifier = "Identifier to redact"
    redacted_1 = redact_identifier(identifier, random=False)
    assert fields.validate("rid", redacted_1)
    redacted_2 = redact_identifier(identifier, random=True)
    assert fields.validate("rid", redacted_2)
    assert redacted_2 != redacted_1
