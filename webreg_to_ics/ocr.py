import pytesseract.pytesseract as pytesseract
from PIL import Image

def image_to_text(image: "Image.Image") -> str:
    return pytesseract.image_to_string(image)
