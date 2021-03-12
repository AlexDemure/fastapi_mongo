from backend.src.apps.statistics.crud import get_count_documents_by_date_today, add_many_documents
from backend.src.apps.statistics.logic import download_statistics_from_dashboard
from backend.src.apps.xlsx.utils import parse_xlsx_to_convert_data_to_dict, convert_xlsx_rows_to_dict, merge_lines
from backend.src.db.database import dashboards_db

from structlog import get_logger


async def upload_statistic_data_to_mongodb(db=dashboards_db):
    """
    Фикстура для загрузки тестовых данных в mongo

    Данная фикстура подходит в качестве функции которая переносит данные из xlsx файла в mongoDB.
    """

    logger = get_logger()
    general_statistics, audiobook_rates_statistic = await download_statistics_from_dashboard(db=db)

    logger.debug("Start upload test data.")
    count_documents = await get_count_documents_by_date_today(db=db)

    # TODO Написать проверку что все записи были записаны в БД
    #  а именно что count_documents == rows_in_xlsx (без учета шапки)
    if count_documents > 0:
        logger.debug(f"Documents found. Skipping loading test data. Count documents today:{count_documents}")
        return

    keys, rows = parse_xlsx_to_convert_data_to_dict(general_statistics)
    converted_current_data = convert_xlsx_rows_to_dict(keys, rows)

    keys, rows = parse_xlsx_to_convert_data_to_dict(audiobook_rates_statistic)
    converted_new_data = convert_xlsx_rows_to_dict(keys, rows)

    converted_data = merge_lines(converted_current_data, converted_new_data)
    if len(converted_data) != 0:
        await add_many_documents(documents=converted_data, db=db)  # Множественная загрузка в БД

    logger.debug(f"Documents is uploaded. Count:{len(converted_data)}")
