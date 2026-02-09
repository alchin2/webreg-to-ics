import os
from scripts.extract_table import extract
from .calendar_ics import create_ics

def main_from_pdf(input_path, output_path="schedule.ics"):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Error: file not found: {input_path}")

    try:
        df = extract(input_path)
    except Exception as e:
        raise RuntimeError(f"Error extracting table from PDF: {e}")

    if df.empty:
        raise ValueError("Error: extracted table is empty")

    create_ics(df, output_path)
    return output_path
