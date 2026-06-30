from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DocumentRecord


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        document_id: str,
        filename: str,
        file_path: str,
        uploaded_at: datetime,
    ) -> DocumentRecord:
        record = DocumentRecord(
            document_id=document_id,
            filename=filename,
            file_path=file_path,
            uploaded_at=uploaded_at,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[DocumentRecord]:
        statement = select(DocumentRecord).order_by(DocumentRecord.uploaded_at.desc())
        return list(self.db.scalars(statement).all())

    def get_by_id(self, document_id: str) -> DocumentRecord | None:
        return self.db.get(DocumentRecord, document_id)

    def delete(self, record: DocumentRecord) -> None:
        self.db.delete(record)
        self.db.commit()


def format_uploaded_at(uploaded_at: datetime) -> str:
    if uploaded_at.tzinfo is None:
        uploaded_at = uploaded_at.replace(tzinfo=timezone.utc)
    return uploaded_at.isoformat().replace("+00:00", "Z")
