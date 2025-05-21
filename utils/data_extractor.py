import re
from typing import Dict, Any
import spacy

nlp = spacy.load("en_core_web_sm")

def parse_invoice_data(text: str) -> Dict[str, Any]:
    data = {
        "invoice_meta": {},
        "items": [],
        "totals": {}
    }

    invoice_no = re.search(r"Invoice\s*(No|Number)[:\s]*([\w\-\/]+)", text, re.IGNORECASE)
    if invoice_no:
        data["invoice_meta"]["invoice_number"] = invoice_no.group(2)

    date_match = re.search(r"Date[:\s]*([\d]{1,2}[\/\-\.][\d]{1,2}[\/\-\.][\d]{2,4})", text, re.IGNORECASE)
    if date_match:
        data["invoice_meta"]["invoice_date"] = date_match.group(1)

    gst_match = re.search(r"GST(?:IN)?[:\s]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})", text)
    if gst_match:
        data["invoice_meta"]["gst_number"] = gst_match.group(1)

    total_match = re.search(r"Total\s+Amount[:\s]*([\d,]+\.?\d*)", text, re.IGNORECASE)
    if total_match:
        data["totals"]["total_amount"] = total_match.group(1)

    gst_total = re.search(r"GST[:\s]*([\d,]+\.?\d*)", text, re.IGNORECASE)
    if gst_total:
        data["totals"]["gst"] = gst_total.group(1)

    lines = text.split('\n')
    item_section = False
    for line in lines:
        if re.search(r"Description|Item|Qty|Rate|Amount", line, re.IGNORECASE):
            item_section = True
            continue
        if item_section and len(line.strip()) > 0:
            item_data = re.findall(r"([\w\s]+?)\s+(\d+)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)", line)
            for desc, qty, rate, amt in item_data:
                data["items"].append({
                    "description": desc.strip(),
                    "quantity": qty,
                    "rate": rate,
                    "amount": amt
                })

    return data
