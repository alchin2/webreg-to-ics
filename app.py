from flask import Flask, render_template, request, send_file
import tempfile
import os

from webreg.pdf_to_image import pdf_to_image
from webreg.ocr import image_to_text
from webreg.parser import parse_lectures
from webreg.calendar import generate_ics

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files.get("pdf")
        if not pdf:
            return "No PDF uploaded", 400

        # save uploaded pdf temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.save(tmp.name)
            pdf_path = tmp.name

        # run your pipeline
        image = pdf_to_image(pdf_path)
        raw_text = image_to_text(image)
        lectures = parse_lectures(raw_text)
        ics_text = generate_ics(lectures, raw_text)

        # save ics temporarily
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
    if not path or not os.path.exists(path):
        return "File not found", 404

    return send_file(path, as_attachment=True, download_name="schedule.ics")


if __name__ == "__main__":
    app.run(debug=True)
