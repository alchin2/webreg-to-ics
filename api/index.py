import sys
import os

# Ensure project root is on sys.path so 'scripts' package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io
import tempfile
from scripts.main_from_pdf import main_from_pdf

app = FastAPI()


def convert_pdf_to_ics(pdf_bytes: bytes) -> bytes:
    tmp_pdf_path = None
    tmp_ics_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf_path = tmp_pdf.name

        with tempfile.NamedTemporaryFile(suffix=".ics", delete=False) as tmp_ics:
            tmp_ics_path = tmp_ics.name

        main_from_pdf(tmp_pdf_path, tmp_ics_path)

        with open(tmp_ics_path, "rb") as f:
            return f.read()
    finally:
        for path in (tmp_pdf_path, tmp_ics_path):
            if path:
                try:
                    os.remove(path)
                except Exception:
                    pass


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    try:
        pdf_bytes = await file.read()
        ics_bytes = convert_pdf_to_ics(pdf_bytes)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")

    return StreamingResponse(
        io.BytesIO(ics_bytes),
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="schedule.ics"'},
    )
