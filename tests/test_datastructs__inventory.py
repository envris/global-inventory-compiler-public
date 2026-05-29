"""Test the Inventory class."""

import pytest

from gic.datastructs import AssociatedValues, DataFrame, Inventory
from gic.datastructs.inventory import NotInInventoryError

DATA_DICTS = [
    {
        "chemical_name": ["Formaldehyde"],
        "generic_id_1": ["Chem1a"],
        "list_tag": ["List 1"],
    },
    {
        "chemical_name": ["DTT"],
        "generic_id_1": ["Chem2a"],
        "list_tag": ["List 1"],
    },
    {
        "chemical_name": ["Acetic acid"],
        "generic_id_1": ["Chem3a"],
        "list_tag": ["List 1"],
    },
    {
        "chemical_name": ["Formalin"],
        "generic_id_1": ["Chem1b"],
        "ec_number": ["200-001-8"],
        "list_tag": ["List 2"],
    },
    {
        "chemical_name": ["Clofenotane"],
        "generic_id_1": ["Chem2b"],
        "ec_number": ["200-024-3"],
        "list_tag": ["List 2"],
    },
    {
        "chemical_name": ["Ethanoic acid"],
        "generic_id_1": ["Chem3b"],
        "ec_number": ["200-580-7"],
        "list_tag": ["List 2"],
    },
    {
        "chemical_name": ["Formaldehyde"],
        "ec_number": ["200-001-8"],
        "list_tag": ["List 3"],
    },
    {
        "chemical_name": ["DTT"],
        "ec_number": ["200-024-3"],
        "list_tag": ["List 3"],
    },
    {
        "chemical_name": ["Acetic acid"],
        "ec_number": ["200-580-7"],
        "list_tag": ["List 3"],
    },
]


@pytest.fixture(name="inventory")
def fixture_inventory() -> Inventory:
    """Basic inventory for testing."""
    df = DataFrame()
    for row_dict in DATA_DICTS:
        ad = AssociatedValues(row_dict)
        ad.clean()
        df.append(ad)
    inv = Inventory()
    inv.import_from_data_frame(df)
    return inv


def test_get_by_sids(inventory: Inventory):
    """Test getting records by SID."""
    assert len(inventory.get_by_sids("generic_id_1", [1])) == 2
    assert len(inventory.get_by_sids("ec_number", [1])) == 1
    assert len(inventory.get_by_sids("chemical_name", [1])) == 2
    assert len(inventory.get_by_sids("list_tag", [1])) == 3
    with pytest.raises(TypeError):
        inventory.get_by_sids("generic_id_1", 1)  # pyright: ignore[reportArgumentType]
    with pytest.raises(ValueError):
        inventory.get_by_sids("not_a_valid_field", [1])


def test_get_by_identifiers(inventory: Inventory):
    """Test getting values by identifier."""
    assert inventory.get_by_identifiers("sid", ["Chem1a"]) == [1]
    assert inventory.get_by_identifiers("list_tag", ["Chem1a"]) == ["List 1"]
    assert inventory.get_by_identifiers("list_tag", ["200-001-8"]) == [
        "List 2",
        "List 3",
    ]
    assert inventory.get_by_identifiers("sid", ["Chem7a"]) == []
    assert inventory.get_by_identifiers("list_tag", ["Chem7a"]) == []
    assert inventory.get_by_identifiers("generic_id_1", ["Chem1a"]) == [
        "Chem1a",
        "Chem1b",
    ]
    with pytest.raises(TypeError):
        assert len(inventory.get_by_identifiers("sid", "Chem1a"))  # pyright: ignore[reportArgumentType]
    with pytest.raises(ValueError):
        inventory.get_by_identifiers("not_a_valid_field", ["Chem1a"])


def test_get_by_list_tags(inventory: Inventory):
    """Test getting sids and identifiers by list tags."""
    df = DataFrame()
    ad = AssociatedValues({"generic_id_1": ["Chem1a"], "list_tag": ["List 4"]})
    ad.clean()
    df.append(ad)
    inventory.import_from_data_frame(df)
    assert inventory.get_by_list_tags("sid", ["List 1", "List 4"]) == [1, 2, 3]
    assert inventory.get_by_list_tags("sid", ["List 1", "List 4"], shared=True) == [1]
    assert inventory.get_by_list_tags("sid", ["List 4"]) == [1]
    assert inventory.get_by_list_tags("generic_id_1", ["List 1", "List 4"]) == [
        "Chem1a",
        "Chem2a",
        "Chem3a",
    ]
    assert inventory.get_by_list_tags(
        "generic_id_1", ["List 1", "List 4"], shared=True
    ) == ["Chem1a"]


def test_by_list_tags_unique(inventory: Inventory):
    """Test getting unique sids and identifiers by list tags."""
    df = DataFrame()
    new_data = [
        {"generic_id_1": ["Chem1a"], "list_tag": ["List 4"]},
        {"generic_id_1": ["Chem4a"], "list_tag": ["List 5"]},
        {"generic_id_1": ["Chem5a"], "list_tag": ["List 5"]},
        {"generic_id_1": ["Chem6a"], "list_tag": ["List 5", "List 6"]},
    ]
    for dic in new_data:
        ad = AssociatedValues(dic)
        ad.clean()
        df.append(ad)
    inventory.import_from_data_frame(df)
    assert inventory.get_by_list_tags_unique("sid", ["List 5"]) == [4, 5]
    assert inventory.get_by_list_tags_unique("generic_id_1", ["List 5"]) == [
        "Chem4a",
        "Chem5a",
    ]
    assert inventory.get_by_list_tags_unique(
        "generic_id_1", ["List 5"], to_ignore=["List 6"]
    ) == ["Chem4a", "Chem5a", "Chem6a"]


def test_fill(inventory: Inventory):
    """Test donating records."""
    df = DataFrame()
    for row_dict in DATA_DICTS:
        ad = AssociatedValues(row_dict)
        ad.clean()
        df.append(ad)
    inventory.fill(df, "list_tag")
    inventory.fill(df, "sid")
    sids = (1, 2, 3, 1, 2, 3, 1, 2, 3)
    for i, row in enumerate(df):
        assert len(row.get_values("list_tag")) == 3
        assert row.get_values("sid")[0] == sids[i]


def test_import_from_data_frame_aux(inventory: Inventory):
    """Test that auxiliary data can be imported."""
    aux_data = [
        {"generic_id_1": ["Chem1a"], "list_tag": ["List 4"]},
        {"generic_id_1": ["Chem7a"], "list_tag": ["List 4"]},
    ]
    df = DataFrame()
    for row_dict in aux_data:
        ad = AssociatedValues(row_dict)
        ad.clean()
        df.append(ad)
    inventory.import_from_data_frame(df, auxiliary=True)
    assert len(inventory.get_sids()) == 3
    assert len(inventory.get_identifiers("generic_id_1")) == 6
    assert "List 4" in inventory.get_by_sids("list_tag", [1])
    assert "List 4" in inventory.get_by_identifiers("list_tag", ["Chem1a"])
    assert "Chem7a" not in inventory.get_identifiers("generic_id_1")


def test_import_from_data_frame_aux_add_identifiers(inventory: Inventory):
    """Test alternative auxiliary mode"""
    aux_data = [
        {"generic_id_1": ["Chem1a"], "cid": ["CID1"], "list_tag": ["List 4"]},
        {"generic_id_1": ["Chem2a"], "cid": ["CID1"], "list_tag": ["List 4"]},
        {
            "generic_id_1": ["Chem6a"],
            "cid": ["CID2"],
            "list_tag": ["List 4"],
        },  # Ignored
    ]
    df = DataFrame()
    for row_dict in aux_data:
        ad = AssociatedValues(row_dict)
        ad.clean()
        df.append(ad)
    inventory.import_from_data_frame(df, auxiliary=True, add_identifiers={"cid"})
    assert len(inventory.get_sids()) == 3
    assert "List 4" in inventory.get_by_sids("list_tag", [1])
    assert "List 4" in inventory.get_by_sids("list_tag", [2])
    assert "CID1" in inventory.get_identifiers("cid")
    assert "CID1" in inventory.get_by_sids("cid", [1])
    assert "CID1" in inventory.get_by_sids("cid", [2])


def test_redact_identifier_type(inventory: Inventory):
    """Test redacting an identifier type."""
    to_redact = set(inventory.get_identifiers("generic_id_1"))
    inventory.redact_identifiers(to_redact, random=False)
    rids_1 = inventory.get_by_sids("rid", [1])
    assert inventory.get_identifiers("generic_id_1") == []
    assert "RID5A5AC1C42FC958FD" in rids_1  # Chem1a
    assert "List 1" in inventory.get_by_sids("list_tag", [1])
    assert "List 1" in inventory.get_by_identifiers("list_tag", ["RID5A5AC1C42FC958FD"])


def test_to_from_jsonl(inventory: Inventory, tmpdir):
    """Make sure saving and loading inventory from file produces same result."""
    inventory.to_jsonl(tmpdir.join("test_inventory1.jsonl"))
    inv2 = Inventory(tmpdir.join("test_inventory1.jsonl"))
    inv2.to_jsonl(tmpdir.join("test_inventory2.jsonl"))
    with open(tmpdir.join("test_inventory1.jsonl"), encoding="utf-8") as f1:
        with open(tmpdir.join("test_inventory2.jsonl"), encoding="utf-8") as f2:
            assert f1.read() == f2.read()


def test_not_in_inventory_error(inventory: Inventory):
    """Test NotInInventoryError is raised appropriately."""
    with pytest.raises(NotInInventoryError):
        inventory.get_by_sids("generic_id_1", [5])
