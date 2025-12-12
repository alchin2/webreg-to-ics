from webreg.pdf_to_image import pdf_to_image
from webreg.ocr import image_to_text
from webreg.parser import parse_lectures
from webreg.calendar import generate_ics


def main():
    pdf_path = input("Enter WebReg PDF path: ").strip()

    image = pdf_to_image(pdf_path)
    text = image_to_text(image)
    lectures = parse_lectures(text)

    ics = generate_ics(lectures, text)

    with open("schedule.ics", "w") as f:
        f.write(ics)

    print("schedule.ics generated successfully")


if __name__ == "__main__":
    main()
