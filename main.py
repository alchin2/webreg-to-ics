from webreg.pdf_extract import extract_table
from webreg.calendar import csv_to_ics


def main():
    pdf_path = input("Enter WebReg PDF path: ").strip()

    # Step 1: extract the course table from the PDF
    csv_path = extract_table(pdf_path)

    # Step 2: generate the ICS calendar from the CSV
    ics_data = csv_to_ics(csv_path)

    # Step 3: save the .ics file
    with open("schedule.ics", "w") as f:
        f.write(ics_data)

    print("✅ schedule.ics generated successfully!")


if __name__ == "__main__":
    main()
