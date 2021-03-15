from datetime import datetime, timedelta, time

from backend.src.overrides import get_datetime_start_day


def prepare_current_data_to_mongo(data: dict, uploaded_at_date_time: datetime = None) -> dict:
    """Подгонка данных под Mongo из XLSX-формата."""
    uploaded_at = get_datetime_start_day() if uploaded_at_date_time is None else uploaded_at_date_time
    return dict(
        isbn=data['isbn'],
        title=data['title'],
        format=data['format'],
        author=data['authors'],
        narrator=data['narrators'],
        imprint=data['imprint'],
        hours=float(data['hours']),
        uploaded_at=uploaded_at,
    )


def prepare_new_data_to_mongo(data: dict = None) -> dict:
    """
    Подгонка данных под Mongo из XLSX-формата.

    data может быть пустая например если:
    из основного дашборда не были найдены данные в новом дашборде.
    """

    if data is None:
        data = {}

    return dict(
        publisher=data.get("publisher", "Storytel Hub"),
        pt=data.get("pt", "E"),
        language=data.get("language", "ru"),
        duration=int(data.get("duration", 0)),
        started=int(data.get("started", 0)),
        c20_rate=float(data.get("c20 rate", 0)),
        c25_rate=float(data.get("c25% rate", 0)),
        finishing_rate=float(data.get("finishing rate", 0)),
    )
