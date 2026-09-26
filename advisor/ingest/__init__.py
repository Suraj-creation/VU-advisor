"""Format-aware ingestion: every adapter turns a source file into SourceUnits (the common IR).

A SourceUnit is a plain dict:
    {"kind": "table_row" | "text_section",
     "source": {"file": <name>, "sheet" | "page": ..., "locator": <cell range | page anchor>},
     "content": {...}}          # table_row: raw cell values; text_section: markdown text

Adding a format (DOCX, PPTX, HTML, CSV, image/OCR) = write `extract(path) -> list[SourceUnit]`
and register it in ADAPTERS. Nothing downstream changes.
"""
from pathlib import Path


def unit(kind, file, locator, content, **where):
    return {"kind": kind, "source": {"file": Path(file).name, **where, "locator": locator}, "content": content}


def adapters():
    from . import excel, pdf
    return {".xlsx": excel.extract, ".pdf": pdf.extract}
