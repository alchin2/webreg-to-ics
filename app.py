from flask import Flask, render_template, request, send_file
import tempfile
import os
import re
from datetime import datetime, timedelta

from webreg.pdf_to_image import pdf_to_image
from webreg.ocr import image_to_text
from webreg.parser import parse_lectures
from webreg.calendar import (
    generate_ics,
    QUARTER_START,
    QUARTER_END,
    weekday_indices,
    parse_time_range,
    EXAM_RE,
)

app = Flask(__name__)

COURSE_RE = re.compile(r"([A-Z]{2,4})\s+(\d+[A-Z]?)")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf = request.files.get("pdf")
        if not pdf:
            return "No PDF uploaded", 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.save(tmp.name)
            pdf_path = tmp.name

        image = pdf_to_image(pdf_path)
        raw_text = image_to_text(image)
        lectures = parse_lectures(raw_text)

        # ---------- generate ICS ----------
        ics_text = generate_ics(lectures, raw_text)
        ics_path = pdf_path.replace(".pdf", ".ics")
        with open(ics_path, "w") as f:
            f.write(ics_text)

        events = []

        # ---------- weekly lectures ----------
        for row in lectures:
            start_t, end_t = parse_time_range(row["time"])

            for wd in weekday_indices(row["days"]):
                first_day = QUARTER_START + timedelta(
                    (wd - QUARTER_START.weekday()) % 7
                )

                current = first_day
                while current <= QUARTER_END:
                    events.append({
                        "title": f"{row['subject']} {row['number']} Lecture",
                        "start": datetime.combine(current, start_t.time()).isoformat(),
                        "end": datetime.combine(current, end_t.time()).isoformat(),
                    })
                    current += timedelta(days=7)

        # ---------- finals & midterms (ROBUST) ----------
        for line in raw_text.splitlines():
            exam_match = EXAM_RE.search(line)
            if not exam_match:
                continue

            kind, date_str, time_str, bldg, room = exam_match.groups()

            course_match = COURSE_RE.search(line)
            if course_match:
                subject, number = course_match.groups()
                course = f"{subject} {number}"
            else:
                course = "Exam"

            start_t, end_t = parse_time_range(time_str)
            exam_date = datetime.strptime(date_str, "%m/%d/%Y").date()

            events.append({
                "title": f"{course} {kind}",
                "start": datetime.combine(exam_date, start_t.time()).isoformat(),
                "end": datetime.combine(exam_date, end_t.time()).isoformat(),
            })

        return render_template(
            "preview.html",
            events=events,
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
