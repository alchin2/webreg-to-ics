import pytesseract
from PIL.Image import Image


def image_to_text(image: Image) -> str:
    """
    Extract text from a PIL image using Tesseract OCR.
    """
    return pytesseract.image_to_string(image)
