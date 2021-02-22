from decimal import Decimal, ROUND_DOWN
from typing import Union

from backend.src.overrides import get_datetime_start_day


def prepare_current_data_to_mongo(data: dict) -> dict:
    """Подгонка данных под Mongo из XLSX-формата."""
    return dict(
        isbn=data['isbn'],
        title=data['Title'],
        format=data['format'],
        author=data['Authors'],
        narrator=data['Narrators'],
        imprint=data['Imprint'],
        hours=float(data['Hours']),
        uploaded_at=get_datetime_start_day(),
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
        pt=data.get("PT", "E"),
        language=data.get("language", "ru"),
        duration=int(data.get("duration", 0)),
        started=int(data.get("started", 0)),
        c20_rate=float(data.get("C20 rate", 0)),
        c25_rate=float(data.get("C25% rate", 0)),
        finishing_rate=float(data.get("Finishing rate", 0)),
    )
