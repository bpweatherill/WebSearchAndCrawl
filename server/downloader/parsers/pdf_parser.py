from pdfminer.high_level import extract_text
from typing import Optional

def parse_pdf(filepath: str) -> Optional[str]:
    """Extract text from a PDF file."""
    try:
        return extract_text(filepath)
    except Exception:
        return None
