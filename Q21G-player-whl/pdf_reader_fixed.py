# Area: Player AI - Fixed PDF Reader
# PRD: docs/prd-player-ai.md
"""PyMuPDF-based PDF reader with correct RTL Hebrew extraction.

Agno's PDFReader uses pypdf which reverses Hebrew text. This module
uses PyMuPDF (fitz) which handles RTL correctly, then chunks text
into ~2000 char paragraphs matching the original chunk size.
"""
import os
import re
from pathlib import Path
from typing import List

import fitz  # PyMuPDF


def extract_pdf(pdf_path: str) -> List[dict]:
    """Extract pages from a PDF using PyMuPDF (correct RTL).

    Returns list of dicts with 'content', 'name', 'page' keys.
    """
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text and len(text) > 30:  # skip near-empty pages
            pages.append({
                "content": text,
                "name": os.path.basename(pdf_path),
                "page": i + 1,
            })
    doc.close()
    return pages


def chunk_text(text: str, chunk_size: int = 2000,
               overlap: int = 200) -> List[str]:
    """Split text into chunks at paragraph boundaries.

    Tries to split on double-newlines (paragraphs), falls back to
    single newlines, then hard splits at chunk_size.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break

        # Try to split at paragraph boundary
        split_pos = text.rfind("\n\n", start + overlap, end)
        if split_pos == -1:
            split_pos = text.rfind("\n", start + overlap, end)
        if split_pos == -1:
            split_pos = text.rfind(" ", start + overlap, end)
        if split_pos == -1:
            split_pos = end

        chunks.append(text[start:split_pos].strip())
        start = split_pos
        # Skip the separator
        while start < len(text) and text[start] in "\n \t":
            start += 1

    return [c for c in chunks if len(c) > 30]


def extract_and_chunk_pdfs(pdf_dir: str,
                           chunk_size: int = 2000) -> List[dict]:
    """Extract all PDFs from a directory, chunk, and return docs.

    Returns list of dicts with 'content', 'name', 'page', 'chunk' keys.
    """
    pdf_dir = Path(pdf_dir)
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    all_chunks = []

    for pdf in pdfs:
        pages = extract_pdf(str(pdf))
        for page_doc in pages:
            chunks = chunk_text(page_doc["content"], chunk_size)
            for j, chunk in enumerate(chunks):
                all_chunks.append({
                    "content": chunk,
                    "name": page_doc["name"],
                    "page": page_doc["page"],
                    "chunk": j,
                })
    return all_chunks
