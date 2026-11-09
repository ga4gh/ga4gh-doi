import csv
import io
import json
from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.doi import Doi, PostedContentRowInput, StandardRowInput
from src.services.suffix_generator import generateSuffix

STANDARDS_CSV_COLUMNS = [
    "month", "day", "year", "item_number", "doi", "publisher_place",
    "std_designator", "standards_body_acronym", "depositor_name", "registrant",
    "publisher_name", "standards_body_name", "organization", "title",
    "abstract_title", "abstract", "contributors",
    "resource", "email_address", "doi_batch_id", "timestamp",
]

POSTED_CONTENT_CSV_COLUMNS = [
    "posted_month", "posted_day", "posted_year",
    "acceptance_month", "acceptance_day", "acceptance_year",
    "doi", "group_title", "title", "original_language_title", "original_language_title_lang",
    "posted_content_type", "contributors", "institution", "citations",
    "resource", "depositor_name", "registrant", "email_address", "doi_batch_id", "timestamp",
]


def read_optional_cell(df, j, column):
    """Read an optional CSV cell, treating a missing column or NaN as empty."""
    if column not in df.columns:
        return ""
    value = df[column][j]
    return "" if str(value) == "nan" else str(value)


def read_json_cell(df, j, column, default):
    """Read a CSV cell as JSON, returning `default` if the cell is empty or invalid."""
    raw = read_optional_cell(df, j, column)
    if not raw:
        return default
    try:
        return json.loads(raw)
    except ValueError:
        return default


def format_authors(contributors_json):
    """Turn the CSV's JSON contributors list into a human-readable "First Last, First Last" string."""
    if not contributors_json:
        return ""
    try:
        contributors = json.loads(contributors_json)
    except ValueError:
        return ""

    names = []
    for contributor in contributors:
        full_name = " ".join(part for part in (contributor.get("first_name", ""), contributor.get("last_name", "")) if part)
        if full_name:
            names.append(full_name)
    return ", ".join(names)


def _wrapped_header(columns: List[str]) -> List[str]:
    return [f"<{column}>" for column in columns]


def build_standards_template() -> str:
    buffer = io.StringIO()
    csv.writer(buffer).writerow(_wrapped_header(STANDARDS_CSV_COLUMNS))
    return buffer.getvalue()


def build_posted_content_template() -> str:
    buffer = io.StringIO()
    csv.writer(buffer).writerow(_wrapped_header(POSTED_CONTENT_CSV_COLUMNS))
    return buffer.getvalue()


def generate_unique_doi(session: Session) -> str:
    while True:
        doi_value = f"10.59756/{generateSuffix()}"
        exists = session.execute(select(Doi).where(Doi.doi == doi_value)).first()
        if not exists:
            return doi_value


def _non_empty_contributors(contributors: List[dict]) -> List[dict]:
    """Drop any contributor with neither a first nor last name."""
    return [c for c in contributors if c.get("first_name") or c.get("last_name")]


def build_standards_csv(rows: List[StandardRowInput], batch_id: str, now: datetime, session: Session) -> str:
    timestamp = now.strftime("%Y%m%d%H%M")
    csv_rows = [_wrapped_header(STANDARDS_CSV_COLUMNS)]

    for row in rows:
        try:
            publish_date = datetime.fromisoformat(row.publish_date)
        except ValueError as exc:
            raise ValueError(f"Invalid publish date: {row.publish_date!r}") from exc

        contributors = _non_empty_contributors(row.contributors)

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
            "abstract_title": row.abstract_title,
            "abstract": row.abstract,
            "contributors": json.dumps(contributors) if contributors else "",
            "resource": row.resource_url,
            "email_address": row.email_address,
            "doi_batch_id": batch_id,
            "timestamp": timestamp,
        }
        csv_rows.append([values[column] for column in STANDARDS_CSV_COLUMNS])

    buffer = io.StringIO()
    csv.writer(buffer).writerows(csv_rows)
    return buffer.getvalue()


def build_posted_content_csv(rows: List[PostedContentRowInput], batch_id: str, now: datetime, session: Session) -> str:
    timestamp = now.strftime("%Y%m%d%H%M")
    csv_rows = [_wrapped_header(POSTED_CONTENT_CSV_COLUMNS)]

    for row in rows:
        try:
            posted_date = datetime.fromisoformat(row.posted_date)
        except ValueError as exc:
            raise ValueError(f"Invalid posted date: {row.posted_date!r}") from exc

        acceptance_date = None
        if row.acceptance_date:
            try:
                acceptance_date = datetime.fromisoformat(row.acceptance_date)
            except ValueError as exc:
                raise ValueError(f"Invalid acceptance date: {row.acceptance_date!r}") from exc

        contributors = _non_empty_contributors(row.contributors)

        values = {
            "posted_month": posted_date.month,
            "posted_day": posted_date.day,
            "posted_year": posted_date.year,
            "acceptance_month": acceptance_date.month if acceptance_date else "",
            "acceptance_day": acceptance_date.day if acceptance_date else "",
            "acceptance_year": acceptance_date.year if acceptance_date else "",
            "doi": generate_unique_doi(session),
            "group_title": row.group_title,
            "title": row.title,
            "original_language_title": row.original_language_title,
            "original_language_title_lang": row.original_language_title_lang,
            "posted_content_type": row.posted_content_type,
            "contributors": json.dumps(contributors) if contributors else "",
            "institution": json.dumps(row.institution) if row.institution else "",
            "citations": json.dumps(row.citations) if row.citations else "",
            "resource": row.resource_url,
            "depositor_name": row.depositor_name,
            "registrant": row.registrant,
            "email_address": row.email_address,
            "doi_batch_id": batch_id,
            "timestamp": timestamp,
        }
        csv_rows.append([values[column] for column in POSTED_CONTENT_CSV_COLUMNS])

    buffer = io.StringIO()
    csv.writer(buffer).writerows(csv_rows)
    return buffer.getvalue()
