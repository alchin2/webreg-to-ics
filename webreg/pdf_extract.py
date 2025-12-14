import os
import tempfile
import pymupdf as fitz


def extract_table(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    page = doc[0]

    page.set_cropbox((45, 50, 612 - 45, 792 - 50))

    tables = page.find_tables() # type: ignore
    if not tables.tables:
        raise ValueError("No tables found in PDF")

    df = tables.tables[0].to_pandas()

    out_path = os.path.join(tempfile.gettempdir(), "schedule.csv")
    df.to_csv(out_path, index=False)
    return out_path
