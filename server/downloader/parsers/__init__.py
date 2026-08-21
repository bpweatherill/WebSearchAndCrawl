# Parsers Module
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def parse_file(filepath: str) -> Optional[str]:
    """Parse a file based on its extension."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    try:
        if suffix == ".pdf":
            from .pdf_parser import parse_pdf
            return parse_pdf(filepath)
        elif suffix == ".docx":
            from .docx_parser import parse_docx
            return parse_docx(filepath)
        elif suffix in (".xls", ".xlsx"):
            from .xlsx_parser import parse_xlsx
            return parse_xlsx(filepath)
        elif suffix == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        else:
            logger.warning(f"Unsupported file type: {suffix}")
            return None
    except Exception as e:
        logger.error(f"Failed to parse {filepath}: {e}")
        return None
