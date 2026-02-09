# webreg-to-ics

Generate a calendar (.ics) file from a course schedule PDF and view your schedule in a web interface.

## Overview
This project extracts course schedule data from a PDF and converts it into an iCalendar (.ics) file. It also provides a simple frontend for viewing your schedule.

## Features
- Parses course schedule PDFs
- Supports lectures, labs, discussions, finals, and midterms
- Handles recurring events with holidays excluded
- Outputs a standards-compliant `.ics` file
- Static web frontend for schedule visualization

## Project Structure

```
webreg-to-ics/
├── README.md                
├── scripts/                 
│   ├── calendar_ics.py      # PDF to ICS conversion
│   ├── extract_table.py     # PDF Extraction logic
│   ├── util.py              # Helper for parsing
│   └── main_from_pdf.py     # Entrypoint            
├── static/                  
│   ├── index.html           
│   ├── script.js            
│   └── style.css            
├── requirements.txt         
└── server.py                # Backend server

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies
- Modern web browser
```

## Usage

## Backend: Generate ICS File

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the script:
   ```
   python scripts/calendar_ics.py <input_pdf>
   ```
   - `<input_pdf>`: Path to your course schedule PDF

3. The output file `schedule.ics` will be created in the project directory.

### Frontend: View Schedule

1. Open the `static/index.html` file in your web browser.

   - The frontend uses `static/script.js` and `static/style.css` for interactivity and styling.
   - If you want to serve the frontend via a local server, run:
     ```
     cd static
     python -m http.server 8000
     ```
     Then visit [http://localhost:8000](http://localhost:8000) in your browser.

2. To display your schedule, you may need to manually upload or parse the generated `schedule.ics` file in the frontend, depending on the implementation.

## Notes
- Holidays are automatically excluded from recurring events.
- Currently tuned to Winter2026

## License
MIT License

