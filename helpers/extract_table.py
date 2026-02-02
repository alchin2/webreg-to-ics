import pymupdf as fitz


def extract(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]

    page.set_cropbox((45, 50, 612 - 45, 792 - 50))

    tables = page.find_tables() # type: ignore
    if not tables.tables:
        raise ValueError("No tables found in PDF")

    df = tables.tables[0].to_pandas()
    print(df)

    return df

