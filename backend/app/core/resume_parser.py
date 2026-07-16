import io
from pypdf import PdfReader
from docx import Document


def extract_text_from_file(file_bytes: bytes, file_name: str) -> str:
    if file_name.lower().endswith(".pdf"):
        return _extract_from_pdf(file_bytes)
    elif file_name.lower().endswith(".docx"):
        return _extract_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")


def _extract_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text_parts).strip()


def _extract_from_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    text_parts = [paragraph.text for paragraph in document.paragraphs]
    return "\n".join(text_parts).strip()
