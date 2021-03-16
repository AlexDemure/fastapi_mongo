from datetime import datetime
from typing import Optional

from backend.src.apps.statistics.pipelines import (
    pipeline_for_episodes, pipeline_for_analytics,
    pipeline_for_diagram, pipeline_for_total_data
)
from backend.src.db.database import dashboards_db
from backend.src.overrides import get_datetime_start_day


def common_filter(books: list, start_date: datetime = None, end_date: datetime = None):
    """Функция для генерирования фильтров для табличных данных и данных для диаграмм."""
    filters = []  # $match фильтры для поиска данных

    isbn_filter = {'isbn': {'$in': books}}  # Поиск книг по isbn
    filters.append(isbn_filter)

    if start_date is not None and end_date is not None:  # Фильтрация по промежутку дат.
        date_filter = {
            "uploaded_at": {
                '$gte': start_date,
                '$lte': end_date
            }
        }
        filters.append(date_filter)

    return filters


async def get_count_documents_by_date_today(db=dashboards_db):
    """Поиск загруженных документов за сегодняшний день."""
    return await db.collection.count_documents({'uploaded_at': get_datetime_start_day()})


async def add_many_documents(documents: list, db=dashboards_db):
    """Множественная загрузка документов за один заход."""
    await db.collection.insert_many(documents)  # Множественная загрузка в БД


async def add_document(document: dict, db=dashboards_db):
    """Добавление одного документа."""
    await db.collection.insert_one(document)


async def get_document_by_key(key: str, db=dashboards_db):
    """Получение одного документа по ключу."""
    return await db.collection.find_one_and_delete({key: {'$ne': None}})


async def get_total_data_by_period(books: list, period: datetime = None, db=dashboards_db) -> Optional[dict]:
    """Получение данных за весь период."""
    filters = [
        {
            'isbn': {
                "$in": books
            }
        },
        {
            'uploaded_at': {
                "$lte": period if period is not None else get_datetime_start_day()
            }
        }
    ]

    async for document in db.collection.aggregate(pipeline_for_total_data(filters)):
        return document


async def get_diagram_data_by_periods(
        books: list,
        start_date: datetime = None,
        end_date: datetime = None,
        db=dashboards_db
) -> list:
    """Получение данных за промежуток времени для данных в виде диаграммы."""
    documents = []  # Найденые документы

    filters = common_filter(books, start_date, end_date)  # Получение фильтров

    # Получение записей с offset и limit
    async for document in db.collection.aggregate(pipeline_for_diagram(filters)):
        documents.append(document)

    return documents


async def get_table_data_by_episodes(
        books: list,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 10,
        offset: int = 0,
        db=dashboards_db

) -> tuple:
    """Получение табличных данных для таблицы со списком эпизодов."""
    documents = []  # Найденые документы

    filters = common_filter(books, start_date, end_date)  # Получение фильтров

    # Получение общего количество записей без offset и limit
    total_rows = await db.collection.count_documents({"$and": filters})

    # Получение записей с offset и limit
    async for document in db.collection.aggregate(pipeline_for_episodes(filters, offset, limit)):
        documents.append(document)

    return total_rows, documents


async def get_table_data_by_analytics(
        books: list,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 10,
        offset: int = 0,
        db=dashboards_db

) -> tuple:
    """Получение табличных данных для таблицы с аналитикой."""
    documents = []  # Найденые документы

    filters = common_filter(books, start_date, end_date)  # Получение фильтров

    # Получение общего количество записей без offset и limit
    total_rows = await db.collection.count_documents({"$and": filters})

    # Получение записей с offset и limit
    async for document in db.collection.aggregate(pipeline_for_analytics(filters, offset, limit)):
        documents.append(document)

    return total_rows, documents









