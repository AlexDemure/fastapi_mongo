from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, root_validator


class BaseParams(BaseModel):
    """Базовая body-схема для получения данных за все время."""
    books: list

    @root_validator
    def check_values(cls, values):
        assert len(values["books"]) > 0, "List is empty."
        return values

    class Config:
        schema_extra = {
            "example": {
                "books": [
                    "0405010081641", "0405010087919", "0405010083614",
                    "0405010083416", "0405010083348", "0405010075442",
                ]
            }
        }


class TablesParams(BaseParams):
    """Табличная body-схема для табличных данных с пагинацией и фильтром по датам."""

    limit: int = None
    offset: int = None
    start_date: datetime = None
    end_date: datetime = None

    @root_validator
    def check_values(cls, values):
        assert len(values["books"]) > 0, "List is empty."

        limit = values.get("limit", None)
        offset = values.get("offset", None)

        if limit is not None:
            assert offset is not None, "Offset is not set."

        if offset is not None:
            assert limit is not None, "Limit is not set."

        if values.get("end_date", None) is not None:
            assert values.get("start_date", None) is not None, "Start date is not set."

        return values


class TotalData(BaseModel):
    total_hours_listened: Decimal = Decimal("0")
    hours_listened_in_week: Decimal = Decimal("0")
    total_listeners: Decimal = Decimal("0")
    listeners_in_week: Decimal = Decimal("0")
    average_listening_percentage: Decimal = Decimal("0")
    average_listening_in_week: Decimal = Decimal("0")
