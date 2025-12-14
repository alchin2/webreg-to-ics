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

from http.server import BaseHTTPRequestHandler
from io import BytesIO
import urllib.parse


class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function handler.
    
    This class bridges Vercel's BaseHTTPRequestHandler interface with Flask's WSGI interface.
    It converts the HTTP request to WSGI environ format, calls the Flask app,
    and writes the response back through the handler's response methods.
    """
    
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def do_PUT(self):
        self._handle_request()
    
    def do_DELETE(self):
        self._handle_request()
    
    def do_PATCH(self):
        self._handle_request()
    
    def do_OPTIONS(self):
        self._handle_request()
    
    def _handle_request(self):
        """Internal method to handle all HTTP methods by converting to WSGI and calling Flask"""
        try:
            # Parse path and query string
            path_parts = self.path.split('?', 1)
            path_info = path_parts[0]
            query_string = path_parts[1] if len(path_parts) > 1 else ''
            
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Build WSGI environ dictionary
            environ = {
                'REQUEST_METHOD': self.command,
                'SCRIPT_NAME': '',
                'PATH_INFO': path_info,
                'QUERY_STRING': query_string,
                'CONTENT_TYPE': self.headers.get('Content-Type', ''),
                'CONTENT_LENGTH': str(len(body)),
                'SERVER_NAME': self.server.server_name if hasattr(self.server, 'server_name') else 'localhost',
                'SERVER_PORT': str(self.server.server_port) if hasattr(self.server, 'server_port') else '80',
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'https',
                'wsgi.input': BytesIO(body),
                'wsgi.errors': BytesIO(),
                'wsgi.multithread': False,
                'wsgi.multiprocess': True,
                'wsgi.run_once': False,
            }
            
            # Add HTTP headers to environ (WSGI format: HTTP_* prefix)
            for key, value in self.headers.items():
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
                if chunk:
                    response_parts['body'].append(chunk)
            
            # Parse status code
            status_code = int(response_parts['status'].split()[0])
            
            # Send response
            self.send_response(status_code)
            
            # Send headers
            for header_name, header_value in response_parts['headers']:
                self.send_header(header_name, header_value)
            self.end_headers()
            
            # Send body
            body_content = b''.join(response_parts['body'])
            self.wfile.write(body_content)
            
        except Exception as e:
            # Error handling
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            import json
            error_response = json.dumps({'ok': False, 'error': f"Handler error: {str(e)}"})
            self.wfile.write(error_response.encode('utf-8'))

# -------------------------------------------------
# Local dev entrypoint
# -------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
