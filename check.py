# check.py
import sqlite3

conn = sqlite3.connect("invoices.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(invoices);")
print("Invoices columns:", cursor.fetchall())

cursor.execute("PRAGMA table_info(invoice_items);")
print("Invoice Items columns:", cursor.fetchall())
