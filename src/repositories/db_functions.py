from typing import Any

from src.models.batch import Batch
from src.models.doi import Doi, Standard, Conference, Article, Grant, PostedContent, ReportWorkingPaper

from sqlalchemy.orm import Session, selectinload, raiseload
from sqlalchemy.exc import OperationalError
from sqlalchemy import func, and_, or_, select
from sqlalchemy.sql import literal_column

class DBFunctions:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, entity: Any) -> None:
        self.db.add(entity)
        self.db.flush()
        #return entity.doi
    
    def commit_to_db(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def close(self) -> None:
        self.db.close()