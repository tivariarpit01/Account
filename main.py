# backend/main.py

from fastapi import FastAPI
from database.database import engine, Base
from routes import invoice  # routes/invoice.py should define `router`

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include your invoice router
app.include_router(invoice.router)
