# backend/main.py
from fastapi import FastAPI
from database.database import engine, Base

from models import Invoice, InvoiceItem
from routes import invoice  # your existing routes import

app = FastAPI()# backend/main.py

from fastapi import FastAPI
from database.database import engine, Base
from models import Invoice, InvoiceItem
from routes import invoice  # import your invoice routes

# Create FastAPI app
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include your router correctly inside the app
app.include_router(invoice.router)


# Create tables
Base.metadata.create_all(bind=engine)

# Include your invoice router
app.include_router(invoice.router)
