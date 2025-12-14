import os
import tempfile
from datetime import datetime, timedelta, date

import pandas as pd
from flask import Flask, request, jsonify, render_template

from webreg.pdf_extract import extract_table
from webreg.calendar import (
    csv_to_ics,
    parse_time_range,
    weekday_indices,
    QUARTER_END,
)

# -------------------------------------------------
# App setup
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# -------------------------------------------------
# Preview settings
# -------------------------------------------------

# First instructional week of January (Monday)
PREVIEW_START = date(2026, 1, 5)

# -------------------------------------------------
# Preview builder
# -------------------------------------------------

def build_calendar_preview(csv_path: str):
    df = pd.read_csv(csv_path)
    df.columns = [c.replace("\n", " ").strip() for c in df.columns]

    events = []
    current_course = None

    for _, row in df.iterrows():
        subject = str(row.get("Subject Course", "")).strip()
        course_type = str(row.get("Type", "")).strip()
        days = str(row.get("Days", "")).strip()
        time = str(row.get("Time", "")).strip()
        bldg = str(row.get("BLDG", "")).strip()
        room = str(row.get("Room", "")).strip()

        # Track course name like calendar.py
        if subject and subject.lower() != "nan":
            current_course = subject

        if not current_course or not time:
            continue

        # -------------------------------------------------
        # Weekly meetings (lecture / discussion / lab)
        # -------------------------------------------------
        if course_type in {"LE", "DI", "LA"} and days:
            try:
                start_t, end_t = parse_time_range(time)
            except Exception:
                continue

            for wd in weekday_indices(days):
                fc_wd = (wd + 1) % 7  # convert Python weekday → FullCalendar weekday

                events.append({
                    "title": f"{current_course} {course_type}",
                    "daysOfWeek": [fc_wd],
                    "startTime": start_t.time().strftime("%H:%M:%S"),
                    "endTime": end_t.time().strftime("%H:%M:%S"),
                    "startRecur": PREVIEW_START.isoformat(),
                    "endRecur": QUARTER_END.isoformat(),
                })

        # -------------------------------------------------
        # Finals / Midterms (one-off)
        # -------------------------------------------------
        elif course_type in {"FI", "MI"} and " " in days:
            try:
                _, date_str = days.split(" ", 1)
                exam_date = datetime.strptime(date_str.strip(), "%m/%d/%Y").date()
                start_t, end_t = parse_time_range(time)

                label = "Final" if course_type == "FI" else "Midterm"

                events.append({
                    "title": f"{current_course} {label}",
                    "start": datetime.combine(
                        exam_date, start_t.time()
                    ).isoformat(),
                    "end": datetime.combine(
                        exam_date, end_t.time()
                    ).isoformat(),
                    "extendedProps": {
                        "location": f"{bldg} {room}".strip()
                    }
                })
            except Exception:
                continue

    return events

# -------------------------------------------------
# Routes
# -------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    if "pdf" not in request.files:
        return jsonify(ok=False, error="No PDF uploaded"), 400

    pdf = request.files["pdf"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        pdf_path = f.name
        pdf.save(pdf_path)

    try:
        csv_path = extract_table(pdf_path)

        ics_text = csv_to_ics(csv_path)
        preview_events = build_calendar_preview(csv_path)

    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    return jsonify(
        ok=True,
        filename="schedule.ics",
        ics=ics_text,
        events=preview_events,
    )

# -------------------------------------------------
# Vercel handler
# -------------------------------------------------

def handler(request):
    """
    Vercel serverless function handler.
    
    This function bridges Vercel's serverless function format with Flask's WSGI interface.
    It converts the Vercel request object to WSGI environ format, calls the Flask app,
    and converts the WSGI response back to Vercel's expected format.
    """
    from io import BytesIO
    import urllib.parse
    
    try:
        # Build WSGI environ from Vercel request
        path_parts = request.path.split('?', 1)
        path_info = path_parts[0]
        query_string = path_parts[1] if len(path_parts) > 1 else ''
        
        # Parse query string
        if query_string:
            query_string = urllib.parse.unquote(query_string)
        
        # Get request body
        body = request.body
        if isinstance(body, str):
            body = body.encode('utf-8')
        elif body is None:
            body = b''
        
        # Build WSGI environ dictionary
        environ = {
            'REQUEST_METHOD': request.method,
            'SCRIPT_NAME': '',
            'PATH_INFO': path_info,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': request.headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body)),
            'SERVER_NAME': request.headers.get('host', 'localhost').split(':')[0],
            'SERVER_PORT': request.headers.get('host', 'localhost:80').split(':')[-1] if ':' in request.headers.get('host', '') else '80',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(body),
            'wsgi.errors': None,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add HTTP headers to environ (WSGI format: HTTP_* prefix)
        for key, value in request.headers.items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key}'] = value
        
        # Capture response from Flask
        response_parts = {'status': None, 'headers': [], 'body': []}
        
        def start_response(status, response_headers):
            """WSGI start_response callback"""
            response_parts['status'] = status
            response_parts['headers'] = response_headers
        
        # Call Flask app (WSGI application)
        response_body = app(environ, start_response)
        
        # Collect response body chunks
        for chunk in response_body:
            response_parts['body'].append(chunk)
        
        # Build response dict for Vercel
        status_code = int(response_parts['status'].split()[0])
        headers = {k: v for k, v in response_parts['headers']}
        body_content = b''.join(response_parts['body'])
        
        # Decode body if it's bytes
        if isinstance(body_content, bytes):
            # Try to decode as UTF-8, fallback to base64 for binary content
            try:
                body_str = body_content.decode('utf-8')
            except UnicodeDecodeError:
                import base64
                body_str = base64.b64encode(body_content).decode('utf-8')
                headers['Content-Encoding'] = 'base64'
        else:
            body_str = body_content
        
        return {
            'statusCode': status_code,
            'headers': headers,
            'body': body_str
        }
    except Exception as e:
        # Error handling for handler itself
        import json
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': False, 'error': f"Handler error: {str(e)}"})
        }

# -------------------------------------------------
# Local dev entrypoint
# -------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
