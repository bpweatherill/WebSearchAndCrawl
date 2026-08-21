from docx import Document
from typing import Optional

def parse_docx(filepath: str) -> Optional[str]:
    """Extract text from a DOCX file."""
    try:
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception:
        return None
