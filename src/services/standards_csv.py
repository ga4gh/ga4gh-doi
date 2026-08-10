import csv
import io
from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.doi import Doi, StandardRowInput
from src.services.suffix_generator import generateSuffix

STANDARDS_CSV_COLUMNS = [
    "month", "day", "year", "item_number", "doi", "publisher_place",
    "std_designator", "standards_body_acronym", "depositor_name", "registrant",
    "publisher_name", "standards_body_name", "organization", "title",
    "resource", "email_address", "doi_batch_id", "timestamp",
]


def _wrapped_header() -> List[str]:
    return [f"<{column}>" for column in STANDARDS_CSV_COLUMNS]


def build_standards_template() -> str:
    buffer = io.StringIO()
    csv.writer(buffer).writerow(_wrapped_header())
    return buffer.getvalue()


def generate_unique_doi(session: Session) -> str:
    while True:
        doi_value = f"10.59756/{generateSuffix()}"
        exists = session.execute(select(Doi).where(Doi.doi == doi_value)).first()
        if not exists:
            return doi_value


def build_standards_csv(rows: List[StandardRowInput], batch_id: str, now: datetime, session: Session) -> str:
    timestamp = now.strftime("%Y%m%d%H%M")
    csv_rows = [_wrapped_header()]

    for row in rows:
        try:
            publish_date = datetime.fromisoformat(row.publish_date)
        except ValueError as exc:
            raise ValueError(f"Invalid publish date: {row.publish_date!r}") from exc

        values = {
            "month": publish_date.month,
            "day": publish_date.day,
            "year": publish_date.year,
            "item_number": row.item_number,
            "doi": generate_unique_doi(session),
            "publisher_place": row.publisher_place,
            "std_designator": row.std_designator,
            "standards_body_acronym": row.standards_body_acronym,
            "depositor_name": row.depositor_name,
            "registrant": row.registrant,
            "publisher_name": row.publisher_name,
            "standards_body_name": row.standards_body_name,
            "organization": row.organization,
            "title": row.title,
            "resource": row.resource_url,
            "email_address": row.email_address,
            "doi_batch_id": batch_id,
            "timestamp": timestamp,
        }
        csv_rows.append([values[column] for column in STANDARDS_CSV_COLUMNS])

    buffer = io.StringIO()
    csv.writer(buffer).writerows(csv_rows)
    return buffer.getvalue()
