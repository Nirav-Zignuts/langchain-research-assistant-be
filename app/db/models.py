from sqlalchemy import Column, DateTime, String

from app.db.database import Base


class DocumentRecord(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, index=True)
