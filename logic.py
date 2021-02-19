
from db.crud import get_total_data_by_period
from overrides import get_datetime_for_last_week
from schemas import BaseParams, TotalData
from serializer import convert_number_to_decimal


async def collect_total_data(params: BaseParams) -> TotalData:
    """Сбор общий данных."""
    doc_all_time = await get_total_data_by_period(params.books)
    if doc_all_time is None:
        return TotalData()

    doc_last_week = await get_total_data_by_period(params.books, get_datetime_for_last_week())
    if doc_last_week is None:
        doc_last_week = dict()

    return TotalData(
        total_hours_listened=convert_number_to_decimal(doc_all_time['total_hours']),
        hours_listened_in_week=convert_number_to_decimal(
            doc_all_time['total_hours'] - doc_last_week.get('total_hours', 0)
        ),

        total_listeners=convert_number_to_decimal(doc_all_time['total_listeners']),
        listeners_in_week=convert_number_to_decimal(
            doc_all_time['total_listeners'] - doc_last_week.get('total_listeners', 0)
        ),

        average_listening_percentage=convert_number_to_decimal(doc_all_time['avg_finishing'] * 100),
        average_listening_in_week=convert_number_to_decimal(
            (doc_all_time['avg_finishing'] - doc_last_week.get('avg_finishing', 0)) * 100
        ),
    )

