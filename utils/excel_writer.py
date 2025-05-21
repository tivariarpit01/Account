import os
import pandas as pd
from typing import Dict, Any
from datetime import datetime

EXCEL_OUTPUT_DIR = "invoices/structured_excel"
os.makedirs(EXCEL_OUTPUT_DIR, exist_ok=True)

def save_invoice_to_excel(data: Dict[str, Any], original_filename: str) -> str:
    invoice_number = data.get("invoice_meta", {}).get("invoice_number", "NA")
    date_part = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{invoice_number}_{date_part}.xlsx"
    output_path = os.path.join(EXCEL_OUTPUT_DIR, output_filename)

    meta_df = pd.DataFrame.from_dict([data.get("invoice_meta", {})])
    items_df = pd.DataFrame(data.get("items", []))
    totals_df = pd.DataFrame.from_dict([data.get("totals", {})])

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        meta_df.to_excel(writer, sheet_name="Invoice Meta", index=False)
        items_df.to_excel(writer, sheet_name="Items", index=False)
        totals_df.to_excel(writer, sheet_name="Totals", index=False)

    return output_path