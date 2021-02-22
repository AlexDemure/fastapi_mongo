import math

from backend.src.apps.statistics.crud import (
    get_total_data_by_period, get_diagram_data_by_periods,
    get_table_data_by_episodes, get_table_data_by_analytics
)
from backend.src.overrides import get_datetime_for_last_week
from backend.src.schemas.statistics import (
    BaseParams, DiagramParams, DiagramData,
    DiagramPoint, TotalData, TableParams,
    TableDataByEpisodes, TableRowByEpisode,
    TableRowByAnalytics, TableDataByAnalytics
)
from backend.src.utils import convert_number_to_decimal


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


async def collect_diagram_data(params: DiagramParams) -> DiagramData:
    """Сбор данных для диаграммы."""
    documents = await get_diagram_data_by_periods(**params.dict())
    return DiagramData(
        points=[
            DiagramPoint(
                day=x['_id']['uploaded_at'],
                total_hours=convert_number_to_decimal(x['total_hours'])
            ) for x in documents
        ]
    )


async def collect_table_data_by_episodes(params: TableParams) -> TableDataByEpisodes:
    total_rows, documents = await get_table_data_by_episodes(**params.dict())
    return TableDataByEpisodes(
        rows=[
            TableRowByEpisode(**x) for x in documents
        ],
        count_rows=len(documents),
        total_rows=total_rows,
        count_pages=math.ceil(total_rows / params.limit)
    )


async def collect_table_data_by_analytics(params: TableParams) -> TableDataByAnalytics:
    total_rows, documents = await get_table_data_by_analytics(**params.dict())
    return TableDataByAnalytics(
        rows=[
            TableRowByAnalytics(**x) for x in documents
        ],
        count_rows=len(documents),
        total_rows=total_rows,
        count_pages=math.ceil(total_rows / params.limit)
    )
