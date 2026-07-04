import os
import pymupdf

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a given PDF file using PyMuPDF."""
    if not os.path.exists(pdf_path):
        return ""
    try:
        doc = pymupdf.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """Splits text into overlapping chunks."""
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def load_and_chunk_pdf(pdf_path: str) -> list:
    text = extract_text_from_pdf(pdf_path)
    return chunk_text(text)
