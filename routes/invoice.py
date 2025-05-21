from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from datetime import datetime
from database.database import SessionLocal
from models import Invoice, InvoiceItem
from utils.data_extractor import parse_invoice_data
from utils.ocr_parser import extract_text_from_pdf

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-invoice/")
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_file_path = f"temp/{uuid4().hex}_{file.filename}"
    os.makedirs("temp", exist_ok=True)

    # Save file temporarily
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())

    # Extract text (with OCR fallback)
    text = extract_text_from_pdf(temp_file_path)

    # Parse text into structured data
    data = parse_invoice_data(text)

    # Clean up after parsing
    os.remove(temp_file_path)

    # Extract and convert invoice date string to date object
    date_str = data["invoice_meta"].get("invoice_date", "")
    try:
        # Adjust date format to your actual input, example: "dd-mm-yyyy"
        invoice_date = datetime.strptime(date_str, "%d-%m-%Y").date()
    except Exception:
        invoice_date = None  # Or datetime.today().date()

    # Create Invoice DB object with proper date object
    invoice = Invoice(
        invoice_number=data["invoice_meta"].get("invoice_number", "UNKNOWN"),
        date=invoice_date,
        gst_number=data["invoice_meta"].get("gst_number", ""),
        party_name=data["invoice_meta"].get("party_name", "Unknown"),
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Add invoice items
    for item in data.get("items", []):
        try:
            item_obj = InvoiceItem(
                invoice_id=invoice.id,
                item_name=item.get("description", "Item"),
                quantity=int(item.get("quantity", 0)),
                rate=float(str(item.get("rate", 0)).replace(',', '')),
                amount=float(str(item.get("amount", 0)).replace(',', '')),
            )
            db.add(item_obj)
        except Exception as e:
            print(f"Skipping item due to error: {e}")

    db.commit()

    return {"message": "Invoice data saved successfully", "invoice_id": invoice.id}
