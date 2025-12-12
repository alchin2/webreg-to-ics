from pdf2image import convert_from_path
from PIL.Image import Image


def pdf_to_image(pdf_path: str) -> Image:
    """
    Convert the first page of a PDF into a PIL Image.
    """
    images = convert_from_path(pdf_path)
    return images[0]
