"""Test cases for InChIKey field"""

from rdkit import Chem

from gic.fields import FieldTestCases
from gic.fields.inchikey import InChIKeyField

rdk_mol1 = Chem.MolFromSmiles("CCC1(C(=O)NC(=O)NC1=O)C2=CC=CC=C2")
rdk_mol2 = Chem.MolFromSmiles(
    "C[C@H](/C=C/[C@H](C)C(C)C)C1CCC\\2[C@@]1(CCC/C2=C\\C=C/3\\C[C@H](CCC3=C)O)C"
)

inchikey_test_cases = FieldTestCases(
    valid=[
        "WSFSSNUMVMOOMR-UHFFFAOYSA-N",
        "PJJJBBJSCAKJQF-UHFFFAOYSA-N",
        "DDBREPKUVSBGFI-UHFFFAOYSA-N",
        "FWJKNZONDWOGMI-UHFFFAOYSA-N",
        "CMSMOCZEIVJLDB-UHFFFAOYSA-N",
        "WAFIYOULDIWAKR-UHFFFAOYSA-N",
        "YVGGHNCTFXOJCH-UHFFFAOYSA-N",
        "XZIDTOHMJBOSOX-UHFFFAOYSA-N",
        "FMMWHPNWAFZXNH-UHFFFAOYSA-N",
        "VYMDGNCVAMGZFE-UHFFFAOYSA-N",
        "UEJJHQNACJXSKW-UHFFFAOYSA-N",
        "ZPUCINDJVBIVPJ-LJISPDSOSA-N",
        "YVGGHNCTFXOJCH-UHFFFAOYSA-N",
        "IAJILQKETJEXLJ-WMJLAQOENA-N",
        "GVKKJJOMQCNPGB-JTQLQIEISA-N",
    ],
    invalid=[
        "AWSFSSNUMVMOOMR-UHFFFAOYSA-N",
        "WSFSSNUMVMOOMR-UHFFFAOYSB-N",
        "WSFSSNUMVMOOMR-UHFFFAOYTA-N",
        "WSFSSNUMVMOOMR-UHFFFAOYSA-NM",
        "WSFSSNUMVMOOMRUHFFFAOYSAN",
    ],
    valid_formatted=[
        "WSFSSNUMVMOOMR-UHFFFAOYSA-N",
        "PJJJBBJSCAKJQF-UHFFFAOYSA-N",
    ],
    invalid_formatted=[
        "WSFSSNUMVMOOM-UHFFFAOYSA-N",
        "WSFSSNUMVMOOMR-UHFFFAOYS-N",
    ],
    patched=[],
    generated=[
        (rdk_mol1, Chem.MolToInchiKey(rdk_mol1)),
        (rdk_mol2, Chem.MolToInchiKey(rdk_mol2)),
    ],
)


def test_inchikey_field():
    """Test the InChIKeyField with predefined cases"""
    field = InChIKeyField()
    field.test(inchikey_test_cases)
