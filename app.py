from flask import Flask, render_template, request, send_file
import os
import tempfile

from webreg_to_ics.pdf_to_image import pdf_to_image
from webreg_to_ics.ocr import image_to_text
from webreg_to_ics.parser import parse_lectures
from webreg_to_ics.calendar import generate_ics

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files["pdf"]
        if not pdf:
            return "No file uploaded", 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            pdf.save(f.name)
            pdf_path = f.name

        image = pdf_to_image(pdf_path)
        raw_text = image_to_text(image)
        lectures = parse_lectures(raw_text)
        ics_text = generate_ics(lectures, raw_text)

        ics_path = pdf_path.replace(".pdf", ".ics")
        with open(ics_path, "w") as f:
            f.write(ics_text)

        return render_template(
            "preview.html",
            lectures=lectures,
            ics_path=ics_path,
        )

    return render_template("index.html")


@app.route("/download")
def download():
    path = request.args.get("path")
    return send_file(path, as_attachment=True, download_name="schedule.ics")
