import re
from pathlib import Path

from pypdf import PdfReader


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", clean_text(text))
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks or ([clean_text(text)] if text.strip() else [])


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return clean_text("\n".join(pages))


def summarize_text(text: str, max_sentences: int = 4) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", clean_text(text))
    useful = [sentence for sentence in sentences if sentence]
    if not useful:
        return "No readable text was extracted yet."
    return " ".join(useful[:max_sentences])
