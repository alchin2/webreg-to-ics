import pymupdf as fitz  

def extract_table(path: str) -> str:
    doc = fitz.open(path)
    page = doc[0]
    page.set_cropbox((45, 50, 612 - 45, 792 - 50))

    tabs = page.find_tables() # type: ignore
    if not tabs.tables:
        raise ValueError("No tables found in the PDF")

    df = tabs[0].to_pandas()
    out_path = "schedule.csv"
    df.to_csv(out_path, index=False)
    return out_path
