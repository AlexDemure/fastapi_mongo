from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, root_validator

from backend.src.overrides import get_datetime_start_day, get_datetime_for_last_week


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


class DiagramParams(BaseParams):
    """Body-схема для данных в виде диаграмм с фильтром по датам."""
    start_date: datetime = None
    end_date: datetime = None

    @root_validator
    def check_values(cls, values):
        assert len(values["books"]) > 0, "List is empty."

        start_date = values.get("start_date", None)
        end_date = values.get("end_date", None)

        if end_date is not None:
            assert start_date is not None, "Start date is not set."

            end_date = get_datetime_start_day(end_date)
            start_date = get_datetime_start_day(start_date)

            assert end_date > start_date, "Value end_date is less than start_date"

            assert (end_date - start_date).days < 720, "Difference days more than 720"

            # Присваиваем стартовой и конечной дате минимальные часовые значения.
            values['end_date'] = end_date
            values['start_date'] = start_date

        return values

    class Config:
        schema_extra = {
            "example": {
                "books": [
                    "0405010081641", "0405010087919", "0405010083614",
                    "0405010083416", "0405010083348", "0405010075442",
                ],
                "start_date": get_datetime_for_last_week(),
                "end_date": get_datetime_start_day()
            }
        }


class XlsxParams(BaseParams):
    """Body-схема для xlsx данных"""

    limit: int = 10
    offset: int = 0


class TableParams(BaseParams):
    """Body-схема для табличных данных с пагинацией и фильтром по датам."""

    limit: int = 10
    offset: int = 0
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

        start_date = values.get("start_date", None)
        end_date = values.get("end_date", None)

        if end_date is not None:
            assert start_date is not None, "Start date is not set."

            end_date = get_datetime_start_day(end_date)
            start_date = get_datetime_start_day(start_date)

            assert end_date > start_date, "Value end_date is less than start_date"

            assert (end_date - start_date).days < 720, "Difference days more than 720"

            # Присваиваем стартовой и конечной дате минимальные часовые значения.
            values['end_date'] = end_date
            values['start_date'] = start_date

        return values

    class Config:
        schema_extra = {
            "example": {
                "books": [
                    "0405010081641", "0405010087919", "0405010083614",
                    "0405010083416", "0405010083348", "0405010075442",
                ],
                "start_date": get_datetime_for_last_week(),
                "end_date": get_datetime_start_day(),
                "limit": 20,
                "offset": 0
            }
        }


class TotalData(BaseModel):
    total_hours_listened: Decimal = Decimal("0")
    hours_listened_in_week: Decimal = Decimal("0")
    total_listeners: Decimal = Decimal("0")
    listeners_in_week: Decimal = Decimal("0")
    average_listening_percentage: Decimal = Decimal("0")
    average_listening_in_week: Decimal = Decimal("0")


class DiagramPoint(BaseModel):
    day: datetime
    total_hours: Decimal = Decimal("0")


class DiagramData(BaseModel):
    points: List[DiagramPoint]


class TableRowByEpisode(BaseModel):
    isbn: str
    name: str
    duration: Decimal = Decimal("0")
    format: str
    imprint: str
    author: str
    narrator: str


class TableRowByAnalytics(BaseModel):
    isbn: str
    name: str
    duration: Decimal = Decimal("0")
    started: int
    c20: Decimal = Decimal("0")
    c25: Decimal = Decimal("0")
    finished: Decimal = Decimal("0")
    author: str
    publisher: str
    language: str = None
    pt: str


class BaseTableData(BaseModel):
    count_rows: int
    total_rows: int
    count_pages: int


class TableDataByEpisodes(BaseTableData):
    rows: List[TableRowByEpisode]


class TableDataByAnalytics(BaseTableData):
    rows: List[TableRowByAnalytics]
