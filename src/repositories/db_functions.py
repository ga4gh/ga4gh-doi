from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


class DBFunctions:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, entity: Any) -> None:
        self.db.add(entity)
        self.db.flush()

    def commit_to_db(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def close(self) -> None:
        self.db.close()

    def get_all(self, model_class: type[T]) -> list[dict[str, Any]]:
        rows = self.db.execute(select(model_class)).scalars().all()
        return [self.serialize_entity(row) for row in rows]

    def get_all_by_field(self, model_class: type[T], field_name: str, value: Any) -> list[dict[str, Any]]:
        rows = self.db.execute(
            select(model_class).where(getattr(model_class, field_name) == value)
        ).scalars().all()
        return [self.serialize_entity(row) for row in rows]

    def get_one_by_field(self, model_class: type[T], field_name: str, value: Any) -> Optional[T]:
        return self.db.execute(
            select(model_class).where(getattr(model_class, field_name) == value)
        ).scalar_one_or_none()

    @staticmethod
    def serialize_entity(entity: Any) -> dict[str, Any]:
        if entity is None:
            return {}

        data: dict[str, Any] = {}
        for column_name in entity.__table__.columns.keys():
            value = getattr(entity, column_name)
            data[column_name] = DBFunctions.serialize_value(value)
        return data

    @staticmethod
    def serialize_value(value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, (list, tuple)):
            return [DBFunctions.serialize_value(item) for item in value]
        if isinstance(value, dict):
            return {str(key): DBFunctions.serialize_value(item) for key, item in value.items()}
        return str(value)