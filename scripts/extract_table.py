import pdfplumber
import pandas as pd


def extract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        cropped = page.crop((45, 50, page.width - 45, page.height - 50))
        tables = cropped.extract_tables()
        if not tables:
            raise ValueError("No tables found in PDF")
        rows = tables[0]
        headers = [c or "" for c in rows[0]]
        data = [[cell or "" for cell in row] for row in rows[1:]]
        df = pd.DataFrame(data, columns=headers)
        print(df)
        return df

