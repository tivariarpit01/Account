from models import Base
from database.database import engine

Base.metadata.create_all(bind=engine)
print("Database tables created successfully.")
