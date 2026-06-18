from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

doi_type_enum = PgEnum(
    'standard', 'conference', 'articles', 'grants', 'posted_content', 'reports_papers',
    name='doi_type_enum', create_type=False,
)


class Base(DeclarativeBase):
    pass


class DoiType(str, Enum):
    STANDARD = 'standard'
    CONFERENCE = 'conference'
    ARTICLES = 'articles'
    GRANTS = 'grants'
    POSTED_CONTENT = 'posted_content'
    REPORTS_PAPERS = 'reports_papers'


class Batch(Base):
    __tablename__ = "batch"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doi_batch_id: Mapped[str] = mapped_column(String(255), nullable=False)
    deposited_by: Mapped[Optional[str]] = mapped_column(String(255))
    depositor_email: Mapped[Optional[str]] = mapped_column(Text)
    doi_type: Mapped[Optional[str]] = mapped_column(doi_type_enum)
    xml: Mapped[Optional[str]] = mapped_column(Text)
    approved: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    submitted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    successful: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    created_by: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    updated_by: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)


class BatchRequest(BaseModel):
    doi_batch_id: str
    deposited_by: str
    depositor_email: str
    doi_type: DoiType
    approved: bool = False
    successful: bool = False
