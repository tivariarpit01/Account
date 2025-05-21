import pytesseract
import pdfplumber
from PIL import Image
import fitz  # PyMuPDF
import os

EXTRACTED_TEXT_DIR = "invoices/extracted_text"
os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"pdfplumber failed: {e}")

    if not text.strip():
        print("Falling back to OCR using pytesseract...")
        try:
            doc = fitz.open(pdf_path)
            for i, page in enumerate(doc):
                pix = page.get_pixmap()
                img_path = f"/tmp/page_{i}.png"
                pix.save(img_path)
                with Image.open(img_path) as img:
                    text += pytesseract.image_to_string(img)
                os.remove(img_path)
        except Exception as e:
            print(f"OCR processing failed: {e}")

    try:
        filename = os.path.basename(pdf_path) + ".txt"
        output_path = os.path.join(EXTRACTED_TEXT_DIR, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Failed to save extracted text: {e}")

    return text