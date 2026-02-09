from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import io
from scripts.main_from_pdf import main_from_pdf
import tempfile
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def convert_pdf_to_ics(pdf_bytes: bytes) -> bytes:

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
        tmp_pdf.write(pdf_bytes)
        tmp_pdf_path = tmp_pdf.name

    with tempfile.NamedTemporaryFile(suffix='.ics', delete=False) as tmp_ics:
        tmp_ics_path = tmp_ics.name

    main_from_pdf(tmp_pdf_path, tmp_ics_path)

    with open(tmp_ics_path, 'rb') as f:
        ics_content = f.read()
    try:
        os.remove(tmp_pdf_path)
        os.remove(tmp_ics_path)
    except Exception:
        pass
    return ics_content


@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    ics_bytes = convert_pdf_to_ics(pdf_bytes)
    return StreamingResponse(
        io.BytesIO(ics_bytes),
        media_type="text/calendar"
    )
