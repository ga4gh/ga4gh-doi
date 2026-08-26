import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, Response

from src.config.session import get_session
from src.repositories.db_functions import DBFunctions
from src.services.api_functions import (
    convert_csv_or_400,
    fetch_all_json,
    fetch_by_field_json,
    get_batch_or_404,
    record_minted_doi,
    submit_batch_xml_to_crossref,
)
from src.services.csv_to_xml import csv_text_to_standards
from src.services.email_service import (
    send_registration_notification,
    send_rejection_email,
    send_submission_failed_email,
    send_success_email,
)
from src.services.csv_functions import build_standards_csv, build_standards_template
from src.models.batch import ApproveRequest, Batch
from src.models.doi import (
    Article,
    Conference,
    Doi,
    Grant,
    PostedContent,
    ReportWorkingPaper,
    Standard,
    StandardsSubmitRequest,
)

router = APIRouter()


@router.post("/standards/upload")
def upload_standards(file: UploadFile = File(...)):
    csv_text = file.file.read().decode("utf-8")
    _, batch, standards = convert_csv_or_400(csv_text)
    batch.submitted = True
    batch.submitted_at = datetime.now()

    with get_session() as session:
        repo = DBFunctions(session)
        repo.insert(batch)
        for standard in standards:
            repo.insert(standard)

    return {"batch_id": batch.doi_batch_id, "standards_count": len(standards)}


@router.get("/standards/template")
def download_standards_template():
    return Response(
        content=build_standards_template(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=standards_template.csv"},
    )


@router.post("/standards/submit")
def submit_standards_batch(body: StandardsSubmitRequest):
    if not body.standards and not body.csv_text:
        raise HTTPException(status_code=400, detail="No standards to submit")

    now = datetime.now()
    batch_id = str(uuid.uuid4())

    try:
        with get_session() as session:
            if body.csv_text:
                csv_text = body.csv_text
            else:
                try:
                    csv_text = build_standards_csv(body.standards, batch_id, now, session)
                except ValueError as exc:
                    raise HTTPException(status_code=400, detail=str(exc)) from exc

            batch = Batch(
                doi_batch_id=batch_id,
                deposited_by=body.deposited_by,
                depositor_email=body.depositor_email,
                doi_type="standard",
                csv=csv_text,
                approved=False,
                submitted=True,
                submitted_at=now,
                successful=None,
                created_by=body.deposited_by,
                created_at=now,
                updated_by=body.deposited_by,
                updated_at=now,
            )

            xml, _, _ = convert_csv_or_400(csv_text)
            batch.xml = xml

            repo = DBFunctions(session)
            repo.insert(batch)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save batch: {exc}") from exc

    try:
        send_registration_notification(batch.doi_batch_id, batch.csv)
    except Exception as exc:
        print("Error sending registration notification email:", exc)

    return {"batch_id": batch.doi_batch_id}


@router.post("/standards/approve")
def approve_standards(body: ApproveRequest):
    with get_session() as session:
        repo = DBFunctions(session)
        batch = get_batch_or_404(repo, body.batch_id)
        batch.approved = body.approved
        return {"message": "Batch approval updated", "batch_id": body.batch_id}


@router.get("/standards/approve/{batch_id}", response_class=HTMLResponse)
def approve_standards_batch_email(batch_id: str, approver_email: str = None):
    with get_session() as session:
        repo = DBFunctions(session)
        batch = get_batch_or_404(repo, batch_id)

        batch.approved = True

        try:
            batch.successful, crossref_response = submit_batch_xml_to_crossref(batch.xml)
        except Exception as exc:
            batch.successful = False
            raise HTTPException(status_code=502, detail=f"Crossref submission failed: {exc}") from exc

        successful = batch.successful
        depositor_email = batch.depositor_email

        if successful:
            try:
                standards = csv_text_to_standards(batch.csv or "")
                for standard in standards:
                    standard.batch_id = uuid.UUID(batch.doi_batch_id)
                    standard.submitted_at = batch.submitted_at
                    standard.registrant = batch.deposited_by
                    repo.insert(standard)
                    record_minted_doi(repo, standard.doi, batch, approver_email)
            except Exception as exc:
                raise HTTPException(status_code=500, detail=f"Failed to record minted standards: {exc}") from exc

    if not successful:
        try:
            send_submission_failed_email(depositor_email, approver_email, batch_id, crossref_response)
        except Exception as exc:
            print("Error sending submission failed email:", exc)
        return f"<p>Batch {batch_id} was submitted to Crossref but minting failed.</p><pre>{crossref_response}</pre>"

    try:
        send_success_email(depositor_email, batch_id)
    except Exception as exc:
        print("Error sending success email:", exc)

    return f"<p>Batch {batch_id} approved and submitted to Crossref.</p>"


@router.get("/standards/reject/{batch_id}", response_class=HTMLResponse)
def reject_standards_batch_email(batch_id: str):
    with get_session() as session:
        repo = DBFunctions(session)
        batch = get_batch_or_404(repo, batch_id)

        batch.approved = False
        depositor_email = batch.depositor_email

    try:
        send_rejection_email(depositor_email, batch_id)
    except Exception as exc:
        print("Error sending rejection email:", exc)

    return f"<p>Batch {batch_id} has been rejected.</p>"


@router.get("/doi/{doi_type}")
def get_doi_by_type(doi_type: str):
    return fetch_by_field_json(Doi, "doi_type", doi_type)


def _get_all_route(model_class):
    """Build a GET-all route handler for a given ORM model class."""

    def route():
        return fetch_all_json(model_class)

    route.__name__ = f"get_all_{model_class.__tablename__}"
    return route


_GET_ALL_ENDPOINTS = [
    ("/standards", Standard),
    ("/conference", Conference),
    ("/articles", Article),
    ("/grants", Grant),
    ("/posted-content", PostedContent),
    ("/reports", ReportWorkingPaper),
    ("/dois", Doi),
]

for _path, _model_class in _GET_ALL_ENDPOINTS:
    router.add_api_route(_path, _get_all_route(_model_class), methods=["GET"])
