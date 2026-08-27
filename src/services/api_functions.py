"""General-purpose helpers shared across the endpoints in src/routers/apis.py."""

import xml.etree.ElementTree as ET

from fastapi import HTTPException

from src.client.submit_doi import submitDoi
from src.config.session import get_session
from src.models.batch import Batch
from src.models.doi import Status
from src.repositories.db_functions import DBFunctions
from src.services.create_records import CreateRecords
from src.services.csv_to_xml import convert_csv_text_to_xml


def fetch_all_json(model_class):
    """Fetch every row of a model as JSON-serializable dicts."""
    with get_session() as session:
        repo = DBFunctions(session)
        return repo.get_all(model_class)


def fetch_by_field_json(model_class, field_name, value):
    """Fetch rows of a model filtered by a single field, as JSON-serializable dicts."""
    with get_session() as session:
        repo = DBFunctions(session)
        return repo.get_all_by_field(model_class, field_name, value)


def get_batch_or_404(repo, batch_id):
    """Look up a Batch by its doi_batch_id, raising a 404 if it doesn't exist."""
    batch = repo.get_one_by_field(Batch, "doi_batch_id", batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


def convert_csv_or_400(csv_text):
    """Convert CSV text to XML, raising HTTPException(400) on any failure."""
    try:
        result = convert_csv_text_to_xml(csv_text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV file: {exc}") from exc
    if result == 0:
        raise HTTPException(status_code=400, detail="Failed to process CSV file")
    return result


def record_minted_doi(repo, doi_value, batch, approver_email):
    """Insert a `dois` row for a DOI minted via Crossref.

    doi_value: the minted DOI. batch: the Batch it belongs to, used for
    doi_batch_id and doi_type. approver_email: the reviewer who approved it,
    stored as both approver and approver_email.
    """
    doi_record = CreateRecords.create_doi()
    doi_record.doi = doi_value
    doi_record.doi_batch_id = batch.doi_batch_id
    doi_record.approver = approver_email
    doi_record.approver_email = approver_email
    doi_record.doi_type = batch.doi_type
    doi_record.status = Status.APPROVED
    doi_record.successful = True
    repo.insert(doi_record)


def _crossref_reported_failure(response_text):
    """Detect a Crossref-level failure reported inside an HTTP 200 response body.

    The deposit endpoint can return HTTP 200 while the batch itself was rejected -
    Crossref reports that as a <doi_batch_diagnostic> with a non-zero failure_count
    and/or a <record_diagnostic status="Failure">, e.g. an invalid resource URL.
    """
    try:
        root = ET.fromstring(response_text)
    except ET.ParseError:
        return False

    if root.tag != "doi_batch_diagnostic":
        return False

    failure_count = root.findtext("batch_data/failure_count")
    if failure_count is not None and failure_count.strip() != "0":
        return True

    return any(diagnostic.get("status") == "Failure" for diagnostic in root.findall("record_diagnostic"))


def submit_batch_xml_to_crossref(xml_text):
    """Submit XML text to Crossref and return (success, response_text)."""
    status_code, response_text = submitDoi(xml_text or "")
    success = status_code == 200 and not _crossref_reported_failure(response_text)
    return success, response_text
