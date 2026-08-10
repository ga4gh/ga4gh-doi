from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
import uuid

from pydantic import BaseModel
from sqlalchemy import Integer, String, Boolean, DateTime, Text, Date, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.batch import Base, DoiType, doi_type_enum
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

status_enum = PgEnum('Pending', 'Approved', 'Rejected', name='status_enum', create_type=False)


class Status(str, Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'


class Doi(Base):
    __tablename__ = "dois"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doi: Mapped[str] = mapped_column(String(255), nullable=False)
    doi_batch_id: Mapped[str] = mapped_column(String(255), nullable=False)
    approver: Mapped[Optional[str]] = mapped_column(Text)
    approver_email: Mapped[Optional[str]] = mapped_column(Text)
    person_responsible: Mapped[Optional[str]] = mapped_column(Text)
    person_responsible_email: Mapped[Optional[str]] = mapped_column(Text)
    doi_type: Mapped[Optional[str]] = mapped_column(doi_type_enum)
    status: Mapped[Optional[str]] = mapped_column(status_enum)
    successful: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    created_by: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    updated_by: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)


class DoiRequest(BaseModel):
    doi: str
    doi_batch_id: str
    approver: str
    approver_email: str
    person_responsible: str
    person_responsible_email: str
    doi_type: DoiType
    status: Status = Status.PENDING
    successful: bool = False


class Standard(Base):
    __tablename__ = "standards"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doi: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_url: Mapped[Optional[str]] = mapped_column(String(255))
    published_date: Mapped[Optional[datetime]] = mapped_column("published_date", Date)
    item_number: Mapped[Optional[int]] = mapped_column(Integer)
    publisher_place: Mapped[Optional[str]] = mapped_column(Text)
    std_designator: Mapped[Optional[str]] = mapped_column(Text)
    standards_body_acronym: Mapped[Optional[str]] = mapped_column(Text)
    depositor_name: Mapped[Optional[str]] = mapped_column(Text)
    registrant: Mapped[Optional[str]] = mapped_column(Text)
    publisher_name: Mapped[Optional[str]] = mapped_column(Text)
    standards_body_name: Mapped[Optional[str]] = mapped_column(Text)
    organization: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(Text)
    resource_link: Mapped[Optional[str]] = mapped_column(Text)
    email_address: Mapped[Optional[str]] = mapped_column(Text)
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    updated_by: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    version: Mapped[Optional[int]] = mapped_column(Integer)


class StandardRequest(BaseModel):
    doi: str
    resource_url: str
    publish_date: datetime
    item_number: Optional[int] = None
    publisher_place: str
    std_designator: str
    standards_body_acronym: str
    depositor_name: Optional[str] = None
    registrant: str
    publisher_name: str
    standards_body_name: str
    organization: str
    title: str
    resource_link: str
    email_address: str
    batch_id: Optional[uuid.UUID] = None


class StandardRowInput(BaseModel):
    title: str
    resource_url: str
    publish_date: str
    item_number: str = ""
    publisher_place: str
    std_designator: str
    standards_body_acronym: str
    depositor_name: str = ""
    registrant: str
    publisher_name: str
    standards_body_name: str
    organization: str
    email_address: str


class StandardsSubmitRequest(BaseModel):
    standards: List[StandardRowInput] = []
    csv_text: Optional[str] = None
    deposited_by: str
    depositor_email: str


class Conference(Base):
    __tablename__ = "conference"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doi: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_url: Mapped[Optional[str]] = mapped_column(String(255))
    given_name: Mapped[Optional[str]] = mapped_column(Text)
    surname: Mapped[Optional[str]] = mapped_column(Text)
    conference_name: Mapped[Optional[str]] = mapped_column(Text)
    conference_theme: Mapped[Optional[str]] = mapped_column(Text)
    conference_acronym: Mapped[Optional[str]] = mapped_column(Text)
    conference_sponsor: Mapped[Optional[str]] = mapped_column(Text)
    conference_number: Mapped[Optional[int]] = mapped_column(Integer)
    conference_location: Mapped[Optional[str]] = mapped_column(Text)
    conference_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    conference_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    proceedings_title: Mapped[Optional[str]] = mapped_column(Text)
    proceedings_subject: Mapped[Optional[str]] = mapped_column(Text)
    publisher_name: Mapped[Optional[str]] = mapped_column(Text)
    publisher_place: Mapped[Optional[str]] = mapped_column(Text)
    publication_year: Mapped[Optional[int]] = mapped_column(Integer)
    isbn: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resource: Mapped[Optional[str]] = mapped_column(Text)
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))


class ConferenceRequest(BaseModel):
    doi: str
    resource_url: str
    given_name: str
    surname: str
    conference_name: str
    conference_theme: str
    conference_acronym: str
    conference_sponsor: str
    conference_number: int
    conference_location: str
    conference_start_date: datetime
    conference_end_date: datetime
    proceedings_title: str
    proceedings_subject: str
    publisher_name: str
    publisher_place: str
    publication_year: int
    isbn: str
    timestamp: datetime
    resource: str
    batch_id: Optional[uuid.UUID] = None


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doi: Mapped[str] = mapped_column(String(255), nullable=False)
    full_title: Mapped[Optional[str]] = mapped_column(Text)
    abbrev_title: Mapped[Optional[str]] = mapped_column(Text)
    issn: Mapped[Optional[str]] = mapped_column(Text)
    coden: Mapped[Optional[str]] = mapped_column(Text)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    journal_volume: Mapped[Optional[int]] = mapped_column(Integer)
    journal_issue: Mapped[Optional[int]] = mapped_column(Integer)
    article_title: Mapped[Optional[str]] = mapped_column(Text)
    contributors: Mapped[Optional[list]] = mapped_column(JSON)
    pages: Mapped[Optional[int]] = mapped_column(Integer)
    resource: Mapped[Optional[str]] = mapped_column(Text)
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))


class ArticleRequest(BaseModel):
    doi: str
    full_title: str
    abbrev_title: str
    issn: str
    coden: str
    publication_date: datetime
    journal_volume: int
    journal_issue: int
    article_title: str
    contributors: List[dict]
    pages: int
    resource: str
    batch_id: Optional[uuid.UUID] = None


class Grant(Base):
    __tablename__ = "grants"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doi: Mapped[str] = mapped_column(String(255), nullable=False)
    project_title: Mapped[Optional[str]] = mapped_column(Text)
    recipients: Mapped[Optional[list]] = mapped_column(JSON)
    description: Mapped[Optional[str]] = mapped_column(Text)
    statement: Mapped[Optional[str]] = mapped_column(Text)
    identifier: Mapped[Optional[str]] = mapped_column(Text)
    award_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    award_number: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    funding_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    funder_name: Mapped[Optional[str]] = mapped_column(Text)
    funder_id: Mapped[Optional[str]] = mapped_column(Text)
    funding_scheme: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resource: Mapped[Optional[str]] = mapped_column(Text)
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))


class GrantRequest(BaseModel):
    doi: str
    project_title: str
    recipients: List[dict]
    description: str
    statement: str
    identifier: str
    award_amount: Decimal
    award_number: Decimal
    funding_amount: Decimal
    funder_name: str
    funder_id: str
    funding_scheme: str
    start_date: datetime
    end_date: datetime
    resource: str
    batch_id: Optional[uuid.UUID] = None


class PostedContent(Base):
    __tablename__ = "posted_content"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doi: Mapped[str] = mapped_column(String(255), nullable=False)
    group_title: Mapped[Optional[str]] = mapped_column(Text)
    contributors: Mapped[Optional[list]] = mapped_column(JSON)
    title: Mapped[Optional[str]] = mapped_column(Text)
    posted_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    acceptance_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    institution: Mapped[Optional[str]] = mapped_column(Text)
    funders: Mapped[Optional[list]] = mapped_column(JSON)
    program: Mapped[Optional[str]] = mapped_column(Text)
    resource: Mapped[Optional[str]] = mapped_column(Text)
    citations: Mapped[Optional[list]] = mapped_column(JSON)
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))


class PostedContentRequest(BaseModel):
    doi: str
    group_title: str
    contributors: List[dict]
    title: str
    posted_date: datetime
    acceptance_date: datetime
    institution: str
    funders: List[dict]
    program: str
    resource: str
    citations: List[dict]
    batch_id: Optional[uuid.UUID] = None


class ReportWorkingPaper(Base):
    __tablename__ = "reports_papers"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doi: Mapped[str] = mapped_column(String(255), nullable=False)
    contributors: Mapped[Optional[list]] = mapped_column(JSON)
    title: Mapped[Optional[str]] = mapped_column(Text)
    edition_number: Mapped[Optional[str]] = mapped_column(Text)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    publisher_name: Mapped[Optional[str]] = mapped_column(Text)
    publisher_place: Mapped[Optional[str]] = mapped_column(Text)
    institution: Mapped[Optional[list]] = mapped_column(JSON)
    report_number: Mapped[Optional[str]] = mapped_column(Text)
    contract_number: Mapped[Optional[str]] = mapped_column(Text)
    resource: Mapped[Optional[str]] = mapped_column(Text)
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))


class ReportWorkingPaperRequest(BaseModel):
    doi: str
    contributors: List[dict]
    title: str
    edition_number: str
    publication_date: datetime
    publisher_name: str
    publisher_place: str
    institution: List[dict]
    report_number: str
    contract_number: str
    resource: str
    batch_id: Optional[uuid.UUID] = None
