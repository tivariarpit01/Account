from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    party_name = Column(String)
    invoice_number = Column(String, unique=True, index=True)
    date = Column(Date)
    gst_number = Column(String)
    total_amount = Column(Float)
    gst = Column(Float)

    items = relationship("InvoiceItem", back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    item_name = Column(String)
    quantity = Column(Integer)
    rate = Column(Float)
    amount = Column(Float)

    invoice = relationship("Invoice", back_populates="items")
