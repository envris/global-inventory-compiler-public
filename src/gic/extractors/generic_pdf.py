"""Generic PDF extractor."""

from pypdf import PdfReader

from .. import fields
from ..datastructs import AssociatedValues
from .generic import GenericExtractor

_DASH_TRANSLATION_TABLE = str.maketrans(
    {
        "\u058a": "-",  # Armenian hyphen
        "\u05be": "-",  # Hebrew maqaf
        "\u1400": "-",  # Canadian syllabics hyphen
        "\u1806": "-",  # Mongolian todo soft hyphen
        "\u2010": "-",  # Hyphen
        "\u2011": "-",  # Non-breaking hyphen
        "\u2012": "-",  # Figure dash
        "\u2013": "-",  # En dash
        "\u2014": "-",  # Em dash
        "\u2015": "-",  # Horizontal bar
        "\u2043": "-",  # Hyphen bullet
        "\u2212": "-",  # Minus sign
        "\u2e17": "-",  # Double oblique hyphen
        "\u2e1a": "-",  # Hyphen with diaeresis
        "\u2e3a": "-",  # Two-em dash
        "\u2e3b": "-",  # Three-em dash
        "\u2e40": "-",  # Double hyphen
        "\u2e5d": "-",  # Oblique hyphen
        "\u301c": "-",  # Wave dash
        "\u3030": "-",  # Wavy dash
        "\u30a0": "-",  # Katakana-hiragana double hyphen
        "\ufe31": "-",  # Vertical em dash
        "\ufe32": "-",  # Vertical en dash
        "\ufe58": "-",  # Small em dash
        "\ufe63": "-",  # Small hyphen-minus
        "\uff0d": "-",  # Full-width hyphen-minus
    }
)


def _normalise_dashes(text: str) -> str:
    """Replace Unicode dash-like characters with an ASCII hyphen-minus."""
    return text.translate(_DASH_TRANSLATION_TABLE)


class GenericPdfExtractor(GenericExtractor):
    """Extract identifiers from a PDF file."""

    def check(self) -> bool:
        """Check if the extractor is ready."""
        if not self.input_file:
            raise ValueError("No input file specified")
        return True

    def extraction_method(self):
        """Extract identifiers having fixed formats from a PDF file."""
        reader = PdfReader(self.input_file)
        for page in reader.pages:
            text = page.extract_text() or ""
            text = _normalise_dashes(text)
            for block in text.split():
                matched_field = fields.match(block, identifiers_only=True)
                if matched_field is None:
                    continue
                extracted_data = {matched_field: [block]}
                clean_data = self.cleaner.filter_data(extracted_data)
                associated_values = AssociatedValues(clean_data)
                associated_values.import_from_dict(self.constants)
                page_num = (page.page_number or 0) + 1
                associated_values.clean_and_log(self.error_log, page_num)
                self.df.append(associated_values)
