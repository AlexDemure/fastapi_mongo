import argparse
import asyncio
import time
from datetime import datetime
from datetime import time as t

from structlog import get_logger

from backend.src.apps.statistics.crud import get_count_documents_by_date_today, add_many_documents
from backend.src.apps.statistics.settings import DATASTUDIO_LINK, FILE_PATH
from backend.src.apps.statistics.utils import GoogleDataStudio
from backend.src.apps.xlsx.utils import parse_xlsx_to_convert_data_to_dict, convert_xlsx_rows_to_dict, merge_lines
from backend.src.db.database import dashboards_db
from backend.src.utils import get_every_date_in_dates_range_generator


async def download_statistics_from_certain_date(start_date: str, end_date: str, db=dashboards_db) -> None:
    """
    Скачивание файлов статистики из 2-х дашбордов в google data studio.

    Используем selenium, вместо Google Data Studio API, т.к.
    невозможно подключить API к текущему аккаунту из-за ограничений со стороный Storytel.
    :return кортеж, где 1-й эл. - полный путь к файлу с общей статистикой,
    2-й эл. - полный путь к файлу с статистики C20 / C25.
    """

    logger = get_logger()

    dashboards_db.init_connection()

    data_studio = GoogleDataStudio()
    await data_studio.login_to_data_studio(db)  # Заходим в лк google data studio

    for date in get_every_date_in_dates_range_generator(start_date, end_date):

        logger.debug(f"Start upload statistics for {date}.")

        general_statistics = data_studio.download_general_statistics_for_one_day(date=date)

        data_studio.driver.get(DATASTUDIO_LINK)  # Перезагружаем страницу с data studio
        time.sleep(5)

        audiobook_rates_statistic = data_studio.download_audiobook_rates_statistic_for_one_day(date=date)
        count_documents = await get_count_documents_by_date_today(db=db)

        # TODO Написать проверку что все записи были записаны в БД
        #  а именно что count_documents == rows_in_xlsx (без учета шапки)
        if count_documents > 0:
            logger.debug(f"Documents found. Skipping loading test data. Count documents today:{count_documents}")
            continue

        keys, rows = parse_xlsx_to_convert_data_to_dict(general_statistics)
        converted_current_data = convert_xlsx_rows_to_dict(keys, rows)

        keys, rows = parse_xlsx_to_convert_data_to_dict(audiobook_rates_statistic)
        converted_new_data = convert_xlsx_rows_to_dict(keys, rows)

        uploaded_at_date_time = datetime.combine(date, t.min)  # Дата выгрузки статистики для MongoDB
        converted_data = merge_lines(converted_current_data, converted_new_data, uploaded_at_date_time)

        if len(converted_data) != 0:
            await add_many_documents(documents=converted_data, db=db)  # Множественная загрузка в БД

        logger.debug(f"Documents is uploaded. Count:{len(converted_data)}")

        data_studio.driver.get(DATASTUDIO_LINK)  # Перезагружаем страницу с data studio
        time.sleep(5)


async def upload_test_data_to_mongodb(start_date: str, end_date: str, db=dashboards_db):
    """
    Фикстура для загрузки тестовых данных в mongo
    Данная фикстура подходит в качестве функции которая переносит данные из xlsx файла в mongoDB.
    """

    current_dashboard = FILE_PATH + "current_dashboard.xlsx"
    new_dashboard = FILE_PATH + "new_dashboard.xlsx"

    for date in get_every_date_in_dates_range_generator(start_date, end_date):

        print("Start upload test data.")
        count_documents = await get_count_documents_by_date_today(db=db)

        if count_documents > 0:
            print(f"Documents found. Skipping loading test data. Count documents today:{count_documents}")
            continue

        keys, rows = parse_xlsx_to_convert_data_to_dict(current_dashboard)
        converted_current_data = convert_xlsx_rows_to_dict(keys, rows)

        keys, rows = parse_xlsx_to_convert_data_to_dict(new_dashboard)
        converted_new_data = convert_xlsx_rows_to_dict(keys, rows)

        uploaded_at_date_time = datetime.combine(date, t.min)  # Дата выгрузки статистики для MongoDB
        converted_data = merge_lines(converted_current_data, converted_new_data, uploaded_at_date_time)

        await add_many_documents(converted_data, db=db)  # Множественная загрузка в БД
        print(f"Documents is uploaded. Count:{len(converted_data)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-sd', '--start_date', type=str, help='Start date')
    parser.add_argument('-ed', '--end_date', type=str, help='End date')
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        loop.create_task(download_statistics_from_certain_date(args.start_date, args.end_date))
    )
    loop.close()
