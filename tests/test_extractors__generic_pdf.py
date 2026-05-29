"""Test the generic PDF extractor."""

import os

from gic import DataFrame, GenericPdfExtractor

from .utils.workflows import compare_data_frames


def test_pdf_extraction():
    """Test basic functionality of the generic PDF extractor."""
    test_path = os.path.join(
        "tests", "data", "extractors__out", "generic_pdf__test.jsonl"
    )
    golden_path = os.path.join(
        "tests", "data", "extractors__out", "generic_pdf__golden.jsonl"
    )
    errors_test_path = os.path.join(
        "tests", "data", "extractors__out", "generic_pdf__errors_test.tsv"
    )
    errors_golden_path = os.path.join(
        "tests", "data", "extractors__out", "generic_pdf__errors_golden.tsv"
    )
    input_file_path = os.path.join(
        "tests", "data", "extractors__in", "generic_pdf__input_file.pdf"
    )
    extractor = GenericPdfExtractor()
    extractor.input_file = input_file_path
    extractor.output_file = test_path
    extractor.errors_file = errors_test_path
    extractor.constants = {"list_tag": ["test_list_tag"]}
    extractor.extract()

    # Compare test and expected (golden) data frames
    test_data_frame = DataFrame.from_jsonl(test_path)
    golden_data_frame = DataFrame.from_jsonl(golden_path)
    assert compare_data_frames(test_data_frame, golden_data_frame), (
        "DataFrames do not match."
    )

    # Compare test and expected (golden) error logs
    with open(errors_test_path, encoding="utf-8") as test_file:
        test_errors = test_file.read()
    with open(errors_golden_path, encoding="utf-8") as golden_file:
        golden_errors = golden_file.read()
    assert test_errors == golden_errors, "Error logs do not match."

    # Clean up: delete the test output file
    os.remove(test_path)
    os.remove(errors_test_path)
