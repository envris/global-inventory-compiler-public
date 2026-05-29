"""Tests for the AssociatedValues class."""

# pyright: reportAttributeAccessIssue=false

import pytest
from rdkit.Chem.rdchem import Mol

from gic.datastructs import AssociatedValues
from gic.datastructs.utils.error_logger import ErrorLog
from gic.datastructs.utils.exceptions import AssociatedValuesNotReady
from gic.fields import ValidationError


def test_initialisation():
    """Test initialisation of the class."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O", 1],
        "inchikey": [],
    }
    av = AssociatedValues(data_dict)
    assert av.chemical_name == ["Aspirin"]
    assert av.cid == ["CID2244"]
    assert av.rdk_mol == ["CC(=O)Oc1ccccc1C(=O)O", 1]  # deserialise and validate later
    assert not hasattr(av, "inchikey")
    # Object must be decoupled from the input dictionary
    data_dict["chemical_name"].append("Acetylsalicylic acid")
    assert av.chemical_name == ["Aspirin"]


def test_bad_initialisation():
    """Test initialisation with bad data."""
    bad_field_name_dict = {
        "chemical_names": ["Aspirin"],
    }
    with pytest.raises(ValueError):
        AssociatedValues(bad_field_name_dict)
    blank_value_dict = {
        "chemical_name": [],
    }
    with pytest.raises(ValueError):
        AssociatedValues(blank_value_dict)


def test_as_dict():
    """Test converting to a dictionary."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    assert av.as_dict() == data_dict
    with pytest.raises(AssociatedValuesNotReady):
        av.as_dict(serialise=True)  # rdk_mol needs to be deserialised first
    av.clean()
    assert av.as_dict(serialise=True) == data_dict


def test_clean():
    """Test cleaning values."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O", "CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    assert not av.is_clean
    av.clean()
    assert av.is_clean
    assert isinstance(av.rdk_mol[0], Mol)  # deserialised and validated
    assert len(av.rdk_mol) == 1  # Duplicate value removed


def test_bad_clean():
    """Test cleaning with bad data."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["Not a valid SMILES string"],
    }
    av = AssociatedValues(data_dict)
    with pytest.raises(ValidationError):
        av.clean()


def test_clean_and_log():
    """Test cleaning with logging."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": [
            "Not a valid SMILES string",
            "CC(=O)Oc1ccccc1C(=O)O",
            "CC(=O)Oc1ccccc1C(=O)O",
        ],
    }
    av = AssociatedValues(data_dict)
    assert not av.is_clean
    log = ErrorLog()
    av.clean_and_log(log, line_no=1)
    assert av.is_clean
    assert isinstance(av.rdk_mol[0], Mol)  # deserialised and validated
    assert len(av.rdk_mol) == 1  # Duplicate value removed
    # Error logged for the invalid SMILES string
    assert len(log) == 1
    assert log[0].line_no == 1
    assert log[0].field_name == "rdk_mol"
    assert log[0].value == "Not a valid SMILES string"


def test_clean_and_log_no_identifiers():
    """Test cleaning with logging when no values are provided."""
    data_dict = {
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    log = ErrorLog()
    av.clean_and_log(log, line_no=1)
    assert isinstance(av.rdk_mol[0], Mol)  # deserialised and validated
    # Error logged for missing identifiers
    assert len(log) == 1
    assert log[0].line_no == 1
    assert log[0].field_name == ""
    assert log[0].value == ""


def test_copy():
    """Test copying the class."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    av_copy = av.copy()
    assert av.as_dict() == av_copy.as_dict()
    assert av.is_clean == av_copy.is_clean
    # Modifying the copy should not affect the original
    av_copy.chemical_name.append("Acetylsalicylic acid")
    assert av.chemical_name == ["Aspirin"]
    assert av_copy.chemical_name == ["Aspirin", "Acetylsalicylic acid"]
    # Make sure True clean state is copied
    av.clean()
    assert av.is_clean
    av_copy = av.copy()
    assert av.is_clean == av_copy.is_clean


def test_from_json():
    """Test creating an instance from a JSONL string."""
    jsonl_str = (
        '{"chemical_name": ["Aspirin"], "cid": ["CID2244"], '
        '"rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"]}\n'
    )
    av = AssociatedValues.from_json(jsonl_str)
    assert av.chemical_name == ["Aspirin"]
    assert av.cid == ["CID2244"]
    assert isinstance(av.rdk_mol[0], Mol)  # deserialised and validated


def bad_from_json():
    """Test creating an instance from a bad JSONL string."""
    bad_jsonl_str = (
        '{"chemical_name": ["Aspirin"], "cid": ["CID2244"], '
        '"rdk_mol": ["Not a valid SMILES string"]}\n'
    )
    with pytest.raises(ValidationError):
        AssociatedValues.from_json(bad_jsonl_str)


def test_generate():
    """Test generating an instance from a dictionary."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "smiles": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    with pytest.raises(AssociatedValuesNotReady):
        av.generate("rdk_mol")
    av.clean()
    # Should still generate without prerequisites, but not produce any values
    av.generate("inchikey")
    assert not hasattr(av, "inchikey")
    av.generate("rdk_mol")
    assert isinstance(av.rdk_mol[0], Mol)  # deserialised and validated
    av.generate("inchikey")
    assert av.inchikey == ["BSYNRYMUTXBXSQ-UHFFFAOYSA-N"]  # Generated from rdk_mol
    with pytest.raises(ValueError):
        av.generate("ec_number")  # No generator for this field
    with pytest.raises(ValueError):
        av.generate("rdk_mols")  # Bad field name


def test_get_identifiers():
    """Test getting identifiers."""
    data_dict = {
        "sid": [1],
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    with pytest.raises(AssociatedValuesNotReady):
        av.get_identifiers()
    av.clean()
    av.generate("inchikey")
    expected_identifiers = {
        "Aspirin",
        "CID2244",
        "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
    }
    assert set(av.get_identifiers()) == expected_identifiers


def test_get_values():
    """Test getting values."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av = AssociatedValues(data_dict)
    with pytest.raises(ValueError):
        av.get_values("cids")  # Bad field name
    with pytest.raises(AssociatedValuesNotReady):
        av.get_values("cid")
    av.clean()
    assert av.get_values("cid") == ["CID2244"]


def test_set_values():
    """Test setting values."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av = AssociatedValues(data_dict)
    # Bad field name
    with pytest.raises(ValueError):
        av.set_values("rdk_mols", ["CC(=O)Oc1ccccc1C(=O)O"])
    # Bad value
    with pytest.raises(ValidationError):
        av.set_values("rdk_mol", ["Not a valid SMILES string"])
    # Good value
    av.set_values("rdk_mol", ["CC(=O)Oc1ccccc1C(=O)O"])
    assert isinstance(av.rdk_mol[0], Mol)  # deserialised and validated
    # Values should be decoupled from the input list
    chemical_names = ["Aspirin"]
    av.set_values("chemical_name", chemical_names)
    chemical_names.append("CID1234")
    assert av.chemical_name == ["Aspirin"]
    # Values should be overwritten
    av.set_values("chemical_name", ["Acetylsalicylic acid"])
    assert av.chemical_name == ["Acetylsalicylic acid"]


def test_get_fields():
    """Test getting field names."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    assert set(av.get_fields()) == {"chemical_name", "cid", "rdk_mol"}


def test_import_from_dict_overwrite_mode():
    """Test importing values from a dictionary in overwrite mode."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av = AssociatedValues(data_dict)
    new_data_dict = {
        "chemical_name": ["Acetylsalicylic acid"],
        "cid": ["CID1234"],
    }
    av.import_from_dict(new_data_dict, overwrite=True)
    assert av.chemical_name == ["Acetylsalicylic acid"]
    assert av.cid == ["CID1234"]


def test_import_from_dict_append_mode():
    """Test importing values from a dictionary in append mode."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av = AssociatedValues(data_dict)
    new_data_dict = {
        "chemical_name": ["Acetylsalicylic acid"],
        "cid": ["CID1234"],
    }
    av.import_from_dict(new_data_dict, overwrite=False)
    assert av.chemical_name == ["Aspirin", "Acetylsalicylic acid"]
    assert av.cid == ["CID2244", "CID1234"]


def test_import_from_dict_bad_field_name():
    """Test importing values from a dictionary with a bad field name."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av = AssociatedValues(data_dict)
    new_data_dict = {
        "chemical_names": ["Acetylsalicylic acid"],
        "cid": ["CID1234"],
    }
    with pytest.raises(ValueError):
        av.import_from_dict(new_data_dict)


def test_import_from_dict_bad_values_type():
    """Test importing values from a dictionary when values are not lists."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av = AssociatedValues(data_dict)
    new_data_dict = {
        "chemical_name": "Acetylsalicylic acid",  # Bad values type
        "cid": ["CID1234"],
    }
    with pytest.raises(TypeError):
        av.import_from_dict(new_data_dict)


def test_import_from_dict_validate_when_cleaned():
    """Test importing values from a dictionary when the class is already cleaned."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    av.clean()
    invalid_data_dict = {
        "chemical_name": ["Acetylsalicylic acid"],
        "cid": ["CID1234"],
        "rdk_mol": ["Not a valid SMILES string"],  # Bad value
    }
    with pytest.raises(ValidationError):
        av.import_from_dict(invalid_data_dict)
    valid_data_dict = {
        "chemical_name": ["Acetylsalicylic acid"],
        "cid": ["CID1234"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],  # Good value
    }
    av.import_from_dict(valid_data_dict)
    assert isinstance(av.rdk_mol[0], Mol)  # Deserialised and validated


def test_import_from_dict_skip_validate_if_not_cleaned():
    """Test importing values from a dictionary when the class is not cleaned."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av = AssociatedValues(data_dict)
    invalid_data_dict = {
        "chemical_name": ["Acetylsalicylic acid"],
        "cid": ["CID1234"],
        "rdk_mol": ["Not a valid SMILES string"],  # Bad value
    }
    av.import_from_dict(invalid_data_dict)
    assert av.rdk_mol == ["Not a valid SMILES string"]  # Imported without validation


def test_is_identified():
    """Test checking if the class is identified."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av = AssociatedValues(data_dict)
    with pytest.raises(AssociatedValuesNotReady):
        av.is_identified()
    av.clean()
    assert av.is_identified() is True
    av_no_identifiers = AssociatedValues({"rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"]})
    av_no_identifiers.clean()
    assert av_no_identifiers.is_identified() is False


def test_merge_without_clean():
    """Test merging two unclean instances will skip validation."""
    data_dict_1 = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av1 = AssociatedValues(data_dict_1)
    data_dict_2 = {
        "chemical_name": ["Acetylsalicylic acid"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av2 = AssociatedValues(data_dict_2)  # Leave unclean
    merged_av = av1.merge(av2)  # Clean automatically called since av1 is clean
    assert merged_av.chemical_name == ["Aspirin", "Acetylsalicylic acid"]
    assert merged_av.cid == ["CID2244"]
    assert merged_av.rdk_mol == ["CC(=O)Oc1ccccc1C(=O)O"]  # Not deserialised


def test_merge_with_clean():
    """Test merging one cleaned instance and one unclean instance."""
    data_dict_1 = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
    }
    av1 = AssociatedValues(data_dict_1)
    av1.clean()
    data_dict_2 = {
        "chemical_name": ["Acetylsalicylic acid"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av2 = AssociatedValues(data_dict_2)  # Leave unclean
    merged_av = av1.merge(av2)
    assert merged_av.chemical_name == ["Aspirin", "Acetylsalicylic acid"]
    assert merged_av.cid == ["CID2244"]
    assert isinstance(merged_av.rdk_mol[0], Mol)  # Deserialised and validated


def test_reduce_to_fields():
    """Test reducing to a subset of fields."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    # Non-existent or invalid fields should be ignored without errors
    reduced_av = av.reduce_to_fields(
        ["chemical_name", "rdk_mol", "inchikey", "invalid_field"]
    )
    assert hasattr(reduced_av, "chemical_name")
    assert hasattr(reduced_av, "rdk_mol")
    assert not hasattr(reduced_av, "cid")


def test_to_json():
    """Test converting to a JSON string."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    with pytest.raises(AssociatedValuesNotReady):
        av.to_json()  # rdk_mol needs to be deserialised first
    av.clean()
    json_str = av.to_json()
    expected_json_str = (
        '{"chemical_name": ["Aspirin"], "cid": ["CID2244"], '
        '"rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"]}'
    )
    assert json_str == expected_json_str


def test_remove_field():
    """Test removing a field."""
    data_dict = {
        "chemical_name": ["Aspirin"],
        "cid": ["CID2244"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    with pytest.raises(ValueError):
        av.remove_field("cids")  # Bad field name
    av.remove_field("cid")
    assert not hasattr(av, "cid")
    # Removing a non-existent field should not raise an error
    av.remove_field("inchikey")


def test_remove_value():
    """Test removing a specific value from a field."""
    data_dict = {
        "chemical_name": ["Aspirin", "Acetylsalicylic acid"],
        "cid": ["CID2244", "CID1234"],
        "rdk_mol": ["CC(=O)Oc1ccccc1C(=O)O"],
    }
    av = AssociatedValues(data_dict)
    with pytest.raises(AssociatedValuesNotReady):
        av.remove_value("cid", "CID2244")  # Not ready yet
    av.clean()
    with pytest.raises(ValueError):
        av.remove_value("cids", "CID2244")  # Bad field name
    with pytest.raises(TypeError):
        # Bad value type
        av.remove_value("cid", 2244)  # pyright: ignore[reportArgumentType]
    av.remove_value("cid", "CID2244")
    assert av.cid == ["CID1234"]
    av.remove_value("cid", "CID9999")  # Ignore quietly when value does not exist
    # Ignore quietly when valid field does not exist
    av.remove_value("inchikey", "BSYNRYMUTXBXSQ-UHFFFAOYSA-N")
    av.remove_value("cid", "CID1234")
    assert not hasattr(av, "cid")  # Field removed when no values remain
    # Test delete of object value by specifying the value in serialised form
    av.remove_value("rdk_mol", "CC(=O)Oc1ccccc1C(=O)O")
    assert not hasattr(av, "rdk_mol")
