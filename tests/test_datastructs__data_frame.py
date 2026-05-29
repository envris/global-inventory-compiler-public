"""Test DataFrame class."""

import openpyxl
import pytest

from gic.datastructs import AssociatedValues, DataFrame
from gic.datastructs.utils.exceptions import AssociatedValuesNotReady, DataFrameNotReady

from .utils.workflows import compare_data_frames

DATA_DICTS = [
    {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "smiles": ["CC(=O)OC1=CC=CC=C1C(=O)O"],
    },
    {
        "chemical_name": ["Acetylsalicylic acid"],
        "cid": ["CID2244", "CID99999"],  # Test multiple CIDs
        "smiles": ["CC(=O)OC1=CC=CC=C1C(=O)O"],
    },
    {
        "chemical_name": ["Paracetamol"],
        "cid": ["CID1983"],
        "smiles": ["CC(=O)NC1=CC=C(C=C1)O"],
    },
    {
        "chemical_name": ["Fexofenadine"],
        "cid": ["CID2248"],
        "smiles": [
            "CC(C)(C1=CC=C(C=C1)C(CCCN2CCC(CC2)C(C3=CC=CC=C3)(C4=CC=CC=C4)O)O)C(=O)O"
        ],
    },
    {
        "chemical_name": ["Caffeine"],
        "cid": ["CID2519"],
        "smiles": ["CN1C=NC2=C1C(=O)N(C(=O)N2C)C"],
    },
    {
        "chemical_name": ["Chemical without CID"],
        "cid": [],
        "smiles": [],
    },
]

DATA_DICTS_2 = [
    {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "ghs_code": ["H302", "H315", "H319", "H335"],
    },
    {
        "chemical_name": ["Paracetamol"],
        "cid": ["CID1983"],
        "ghs_code": ["H302", "H315", "H319", "H412"],
    },
    {
        "chemical_name": ["Fexofenadine"],
        "cid": ["CID2248"],
        "ghs_code": [],
    },
    {
        "chemical_name": ["Caffeine"],
        "cid": ["CID2519"],
        "ghs_code": ["H302"],
    },
]


@pytest.fixture(name="data_frame")
def fixture_data_frame() -> DataFrame:
    """Basic DataFrame for testing."""
    data = DataFrame()
    for row_dict in DATA_DICTS:
        av = AssociatedValues(row_dict)
        av.clean()
        data.append(av)
    data.generate("rdk_mol")
    data.generate("rdk_rdkfp")
    data.generate("inchi")
    data.generate("inchikey")
    return data


@pytest.fixture(name="data_frame_2")
def fixture_data_frame_2() -> DataFrame:
    """Second DataFrame for testing."""
    data = DataFrame()
    for row_dict in DATA_DICTS_2:
        av = AssociatedValues(row_dict)
        av.clean()
        data.append(av)
    return data


def test_add(data_frame: DataFrame, data_frame_2: DataFrame):
    """Test adding two dataframes."""
    new_data_frame = data_frame + data_frame_2
    assert len(new_data_frame) == len(data_frame) + len(data_frame_2)
    assert new_data_frame[0].as_dict() == data_frame[0].as_dict()
    assert new_data_frame[len(data_frame)].as_dict() == data_frame_2[0].as_dict()


def test_getitem(data_frame: DataFrame):
    """Test list-style indexing and slicing."""
    assert data_frame[1].as_dict() == data_frame.data[1].as_dict()
    assert data_frame[-1].as_dict() == data_frame.data[-1].as_dict()
    assert [row.as_dict() for row in data_frame[1:3]] == [
        row.as_dict() for row in data_frame.data[1:3]
    ]


def test_len(data_frame: DataFrame):
    """Test len() function."""
    assert len(data_frame) == len(data_frame.data)


def test_data_getter(data_frame: DataFrame):
    """Test data property getter. Makes sure its a copy of the internal data."""
    data = data_frame.data
    assert data == data_frame.data
    assert data is not data_frame.data
    original_len = len(data)
    data.append(AssociatedValues({"chemical_name": ["Test Chemical"]}))
    assert len(data) == original_len + 1
    assert len(data_frame) == original_len


def test_append(data_frame: DataFrame):
    """Test appending a row."""
    new_row = AssociatedValues({"chemical_name": ["Test Chemical"]})
    # Should raise an error if the new row is not cleaned before appending
    with pytest.raises(AssociatedValuesNotReady):
        data_frame.append(new_row)
    new_row.clean()
    # Success
    data_frame.append(new_row, ignore_unidentified=True)
    assert len(data_frame) == 7
    # Ignore silently if the new row is not identified
    bad_row = AssociatedValues({"ghs_code": ["H302"]})
    bad_row.clean()
    data_frame.append(bad_row, ignore_unidentified=True)
    assert len(data_frame) == 7
    assert data_frame[-1].as_dict() == new_row.as_dict()


def test_count_empties(data_frame: DataFrame):
    """Test counting empty values in a field."""
    assert data_frame.count_empties("ghs_code") == 6
    assert data_frame.count_empties("chemical_name") == 0
    assert data_frame.count_empties("cid") == 1


def test_to_and_from_jsonl(data_frame: DataFrame, tmpdir):
    """Test JSONL save and load to JSONL round-trip."""
    file_path_1 = tmpdir.join("data_frame_1.jsonl")
    file_path_2 = tmpdir.join("data_frame_2.jsonl")
    data_frame.to_jsonl(file_path_1)
    data_frame_2 = DataFrame.from_jsonl(file_path_1)
    data_frame_2.to_jsonl(file_path_2)
    compare_data_frames(data_frame, data_frame_2)


def test_generate(data_frame_2: DataFrame):
    """Test generating new fields without required fields."""
    with pytest.raises(DataFrameNotReady):
        data_frame_2.generate("rdk_mol")


def test_get_active_fields(data_frame: DataFrame):
    """Test getting active fields."""
    active_fields = data_frame.get_active_fields()
    assert set(active_fields) == {
        "chemical_name",
        "cid",
        "smiles",
        "rdk_mol",
        "rdk_rdkfp",
        "inchi",
        "inchikey",
    }


def test_get_values(data_frame: DataFrame):
    """Test getting values for a field."""
    cid_values = data_frame.get_values("cid")
    assert cid_values == ["CID1983", "CID2244", "CID2248", "CID2519", "CID99999"]


def test_get_values_by_identifiers(data_frame: DataFrame):
    """Test getting values for a field by identifiers."""
    with pytest.raises(DataFrameNotReady):
        data_frame.get_values_by_identifiers("cid", ["Aspirin"])
    data_frame.index_by_identifier("chemical_name")
    cid_values = data_frame.get_values_by_identifiers("cid", ["Aspirin", "Paracetamol"])
    assert cid_values == ["CID1983", "CID2244"]
    cid_values = data_frame.get_values_by_identifiers("cid", ["No Match"])
    assert cid_values == []


def test_index_by_identifier(data_frame: DataFrame):
    """Test indexing by identifier field."""
    assert not data_frame.is_indexed_by_identifier()
    with pytest.raises(ValueError):
        data_frame.index_by_identifier("smiles")
    data_frame.index_by_identifier("chemical_name")
    assert data_frame.is_indexed_by_identifier()


def test_merge_rows_by_field(data_frame: DataFrame):
    """Test merging rows by a field."""
    assert len(data_frame) == 6
    data_frame.merge_rows_by_field("cid")
    assert len(data_frame) == 5


def test_to_csv(data_frame: DataFrame, tmpdir):
    """Test saving to CSV."""
    file_path = tmpdir.join("data_frame.csv")
    data_frame.merge_rows_by_field("cid")
    data_frame.to_csv(file_path)
    with open(file_path) as f:
        lines = f.readlines()
    assert len(lines) == len(data_frame) + 1  # Header + 5 rows


def test_to_xlsx(data_frame: DataFrame, tmpdir):
    """Test saving to XLSX."""
    file_path = tmpdir.join("data_frame.xlsx")
    data_frame.merge_rows_by_field("cid")
    data_frame.to_xlsx(file_path)
    workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    sheet = workbook.active
    assert sheet is not None
    rows = list(sheet.iter_rows(values_only=True))
    workbook.close()

    non_empty_rows = [
        row for row in rows if any(value not in (None, "") for value in row)
    ]

    assert len(non_empty_rows) == len(data_frame) + 1  # Header + 5 rows
