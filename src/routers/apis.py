import os
import tempfile
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select

from src.config.session import get_session
from src.repositories.db_functions import DBFunctions
from src.services.csv_to_xml import CSVtoXML
from src.models.batch import Batch
from src.models.doi import Doi, Standard, Conference, Article, Grant, PostedContent, ReportWorkingPaper

router = APIRouter()


@router.post("/standards/upload")
def upload_standards(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
        tmp_csv.write(file.file.read())
        csv_path = tmp_csv.name

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp_xml:
        xml_path = tmp_xml.name

    try:
        result = CSVtoXML(csv_path, xml_path)
        if result == 0:
            raise HTTPException(status_code=400, detail="Failed to process CSV file")
        _, batch, standards = result
        batch.submitted = True
        batch.submitted_at = datetime.now()
        with get_session() as session:
            repo = DBFunctions(session)
            repo.insert(batch)
            for standard in standards:
                repo.insert(standard)
    finally:
        os.unlink(csv_path)
        if os.path.exists(xml_path):
            os.unlink(xml_path)

    return {"batch_id": batch.doi_batch_id, "standards_count": len(standards)}


class ApproveRequest(BaseModel):
    batch_id: str
    approved: bool
    approver_email: str


@router.post("/standards/approve")
def approve_standards(body: ApproveRequest):
    with get_session() as session:
        batch = session.execute(
            select(Batch).where(Batch.doi_batch_id == body.batch_id)
        ).scalar_one_or_none()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        batch.approved = body.approved
        return {"message": "Batch approval updated", "batch_id": body.batch_id}


@router.get("/doi/{doi_type}")
def get_doi_by_type(doi_type: str):
    with get_session() as session:
        repo = DBFunctions(session)
        return jsonable_encoder(repo.get_all_by_field(Doi, "doi_type", doi_type))


@router.get("/standards")
def get_standards():
    with get_session() as session:
        repo = DBFunctions(session)
        return jsonable_encoder(repo.get_all(Standard))


@router.get("/conference")
def get_conference():
    with get_session() as session:
        repo = DBFunctions(session)
        return jsonable_encoder(repo.get_all(Conference))


@router.get("/articles")
def get_articles():
    with get_session() as session:
        repo = DBFunctions(session)
        return jsonable_encoder(repo.get_all(Article))


@router.get("/grants")
def get_grants():
    with get_session() as session:
        repo = DBFunctions(session)
        return jsonable_encoder(repo.get_all(Grant))


@router.get("/posted-content")
def get_posted_content():
    with get_session() as session:
        repo = DBFunctions(session)
        return jsonable_encoder(repo.get_all(PostedContent))


@router.get("/reports")
def get_reports():
    with get_session() as session:
        repo = DBFunctions(session)
        return jsonable_encoder(repo.get_all(ReportWorkingPaper))


@router.get("/dois")
def get_all_dois():
    with get_session() as session:
        repo = DBFunctions(session)
        return jsonable_encoder(repo.get_all(Doi))
