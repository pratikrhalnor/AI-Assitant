import fitz  # pymupdf
import pytesseract
import os

# Prevent pandas/pyarrow issues
os.environ["PANDAS_USE_PYARROW"] = "0"
from PIL import Image
import io

class PDFLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        doc = fitz.open(self.file_path)
        documents = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            ocr_text = ""

            images = page.get_images(full=True)

            for img in images:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                image = Image.open(io.BytesIO(image_bytes))
                ocr_text += pytesseract.image_to_string(image)

            full_text = text + "\n" + ocr_text

            documents.append({
                "content": full_text,
                "page": page_num
            })

        return documents