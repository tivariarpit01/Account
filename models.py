from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from database.database import Base  

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    party_name = Column(String(100), nullable=False)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    date = Column(Date, nullable=False)  # Use Date type
    gst_number = Column(String(15), nullable=True)
    total_amount = Column(Float, nullable=True)
    gst = Column(Float, nullable=True)

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number='{self.invoice_number}', party='{self.party_name}')>"

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")

    def __repr__(self):
        return f"<InvoiceItem(id={self.id}, item_name='{self.item_name}', quantity={self.quantity})>"
