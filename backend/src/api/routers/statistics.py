import datetime
from fastapi import APIRouter
from starlette.responses import FileResponse

from backend.src.apps.statistics.crud import get_table_data_by_episodes, get_table_data_by_analytics
from backend.src.apps.statistics.logic import (
    collect_total_data, collect_diagram_data,
    collect_table_data_by_analytics, collect_table_data_by_episodes
)
from backend.src.apps.statistics.settings import FILE_PATH
from backend.src.apps.xlsx.utils import prepare_data_from_mongo_for_xlsx, write_data_to_xlsx
from backend.src.schemas.statistics import (
    BaseParams, DiagramParams, TableParams,
    DiagramData, TotalData, TableDataByEpisodes,
    TableDataByAnalytics
)

router = APIRouter()


@router.post("/total/", response_model=TotalData)
async def get_total_data(params: BaseParams):
    """
    Получение данных для таблицы с общими данными.
    - **validation #1**: Список books должен быть больше 0.

    Важно на первую таблицы фильтры с диапозоном дат не применяются.
    """
    return await collect_total_data(params)


@router.post("/diagram/", response_model=DiagramData)
async def get_diagram_data(params: DiagramParams):
    """
    Получение данных для таблицы в виде диаграммы.

    - **validation #1**: Список books должен быть больше 0.
    - **validation #2**: Передавать start_date и end_date вместе
     если будет передано только одно значение фильтры по датам не применятся.
     - **validation #3**: End_date должен быть больше start_date в днях.
     - **validation #4**: Диапозон дат не должен превышать более 720 дней.
    """
    return await collect_diagram_data(params)


@router.post("/episodes/", response_model=TableDataByEpisodes)
async def get_episode_data(params: TableParams):
    """
    Получение табличных данных по эпизодам.

    - **validation #1**: Список books должен быть больше 0.
    - **validation #2**: Передавать start_date и end_date вместе
     если будет передано только одно значение фильтры по датам не применятся.
     - **validation #3**: End_date должен быть больше start_date в днях.
     - **validation #4**: Диапозон дат не должен превышать более 720 дней.
     - **validation #5**: limit и offset можно не передавать,
      по дефолту будет 10 записей и с 0-вым индексом (1 страница).
     Offset - срез записей, если передавать значение 20 тогда будут пропущены первые 20 записей из запроса,
     чтобы передавать номер страницы необходимо высчитывать по формуле limit * number_page.
    """
    return await collect_table_data_by_episodes(params)


@router.post("/analytics/", response_model=TableDataByAnalytics)
async def get_analytics_data(params: TableParams):
    """
    Получение табличных данных по аналитике.

    - **validation #1**: Список books должен быть больше 0.
    - **validation #2**: Передавать start_date и end_date вместе
     если будет передано только одно значение фильтры по датам не применятся.
     - **validation #3**: End_date должен быть больше start_date в днях.
     - **validation #4**: Диапозон дат не должен превышать более 720 дней.
     - **validation #5**: limit и offset можно не передавать,
      по дефолту будет 10 записей и и с 0-вым индексом (1 страница).
     Offset - срез записей, если передавать значение 20 тогда будут пропущены первые 20 записей из запроса,
     чтобы передавать номер страницы необходимо высчитывать по формуле limit * number_page.
    """
    return await collect_table_data_by_analytics(params)


@router.post("/get_episodes_statistics_xlsx/")
async def get_episodes_statistics_xlsx(params: TableParams):
    """
    Получение табличных данных по эпизодам в xlsx файле.

    - **validation #1**: Список books должен быть больше 0.
    - **validation #2**: Передавать start_date и end_date вместе
     если будет передано только одно значение фильтры по датам не применятся.
     - **validation #3**: End_date должен быть больше start_date в днях.
     - **validation #4**: Диапозон дат не должен превышать более 720 дней.
     - **validation #5**: limit и offset можно не передавать,
      по дефолту будет 10 записей и с 0-вым индексом (1 страница).
     Offset - срез записей, если передавать значение 20 тогда будут пропущены первые 20 записей из запроса,
     чтобы передавать номер страницы необходимо высчитывать по формуле limit * number_page.
    """
    total_rows, documents = await get_table_data_by_episodes(**params.dict())
    prepared_data = prepare_data_from_mongo_for_xlsx(documents)

    xlsx_path = FILE_PATH + 'xlsx/' + f'episodes_{datetime.date.today()}.xlsx'
    write_data_to_xlsx(prepared_data, xlsx_path)

    return FileResponse(path=xlsx_path, filename=f'{datetime.date.today()}.xlsx')


@router.post("/get_analytics_statistics_xlsx/")
async def get_analytics_statistics_xlsx(params: TableParams):
    """
    Получение табличных данных по аналитике в xlsx файле.

    - **validation #1**: Список books должен быть больше 0.
    - **validation #2**: Передавать start_date и end_date вместе
     если будет передано только одно значение фильтры по датам не применятся.
     - **validation #3**: End_date должен быть больше start_date в днях.
     - **validation #4**: Диапозон дат не должен превышать более 720 дней.
     - **validation #5**: limit и offset можно не передавать,
      по дефолту будет 10 записей и и с 0-вым индексом (1 страница).
     Offset - срез записей, если передавать значение 20 тогда будут пропущены первые 20 записей из запроса,
     чтобы передавать номер страницы необходимо высчитывать по формуле limit * number_page.
    """
    total_rows, documents = await get_table_data_by_analytics(**params.dict())
    prepared_data = prepare_data_from_mongo_for_xlsx(documents)

    xlsx_path = FILE_PATH + 'xlsx/' + f'analytics_{datetime.date.today()}.xlsx'
    write_data_to_xlsx(prepared_data, xlsx_path)

    return FileResponse(path=xlsx_path, filename=f'{datetime.date.today()}.xlsx')
