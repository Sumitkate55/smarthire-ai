"""
Parses uploaded PDF resumes and extracts raw text.
Uses PyPDF2 for text extraction.
"""
import io

def parse_pdf(file_path: str) -> str:
    """Read a PDF file from disk and return all text content."""
    text_parts = []
    
    # Try pypdf first (modern successor to PyPDF2)
    try:
        import pypdf
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        extracted = "\n".join(text_parts).strip()
        if extracted:
            return extracted
    except Exception:
        pass

    # Fall back to PyPDF2
    text_parts = []
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {e}")
    return "\n".join(text_parts)


def parse_pdf_bytes(file_bytes: bytes) -> str:
    """Parse PDF from bytes (used when file is in-memory)."""
    text_parts = []
    
    # Try pypdf first
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        extracted = "\n".join(text_parts).strip()
        if extracted:
            return extracted
    except Exception:
        pass

    # Fall back to PyPDF2
    text_parts = []
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF bytes: {e}")
    return "\n".join(text_parts)

