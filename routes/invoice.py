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

    # Clean up temp file
    os.remove(temp_file_path)

    # Basic checks
    invoice_meta = data.get("invoice_meta", {}) if data else {}
    invoice_number = invoice_meta.get("invoice_number")

    # If invoice number missing, return warning immediately
    if not invoice_number:
        return {
            "warning": "Invoice data is not in the appropriate format. Please upload a valid invoice."
        }

    # Check if invoice already exists in DB
    existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
    if existing_invoice:
        return {
            "message": "Invoice already exists.",
            "invoice_number": invoice_number,
            "existing_invoice_id": existing_invoice.id
        }

    # Validate other required fields for format
    if (
        not data or
        not invoice_meta or
        not invoice_meta.get("invoice_date") or
        not invoice_meta.get("total_amount") or
        not data.get("items")
    ):
        return {
            "warning": "Invoice data is not in the appropriate format. Please upload a valid invoice."
        }

    # Parse invoice date
    date_str = invoice_meta.get("invoice_date", "")
    try:
        invoice_date = datetime.strptime(date_str, "%d-%m-%Y").date()
    except Exception:
        invoice_date = datetime.today().date()

    # Create new invoice record
    invoice = Invoice(
        invoice_number=invoice_number,
        date=invoice_date,
        gst_number=invoice_meta.get("gst_number", ""),
        party_name=invoice_meta.get("party_name", "Unknown"),
        total_amount=float(invoice_meta.get("total_amount", 0)),
        gst=float(invoice_meta.get("gst", 0))
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

    return {
        "message": "Invoice data saved successfully",
        "invoice_id": invoice.id
    }
