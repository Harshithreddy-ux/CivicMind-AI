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

def load_all_documents_in_directory(directory_path: str) -> list:
    """Scans directory for pdf, md, txt files, reads and chunks them all."""
    if not os.path.exists(directory_path):
        return []
        
    all_text = []
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if not os.path.isfile(filepath):
            continue
            
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            text = extract_text_from_pdf(filepath)
            if text:
                all_text.append(f"Source: {filename}\n{text}")
        elif ext in (".md", ".txt"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                    if text:
                        all_text.append(f"Source: {filename}\n{text}")
            except Exception as e:
                print(f"Error reading text file {filepath}: {e}")
                
    combined_text = "\n\n=== DOCUMENT SPLIT ===\n\n".join(all_text)
    return chunk_text(combined_text)
