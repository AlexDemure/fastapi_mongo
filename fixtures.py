from utils import parse_xlsx, convert_xlsx_rows_to_dict, merge_lines
from db.crud import get_count_documents_by_date_today, add_many_documents


async def upload_test_data_to_mongodb():
    """
    Фикстура для загрузки тестовых данных в mongo

    Данная фикстура подходит в качестве функции которая переносит данные из xlsx файла в mongoDB.
    """

    # TODO РЕАЛИЗАЦИЯ СКРИПТА ДЛЯ СКАЧИВАНИЯ ФАЙЛА ИЗ DASHBOARDS
    # file = download_file_from_dashboard()
    # filepath = file.filepath

    current_dashboard = "static/current_dashboard.xlsx"
    new_dashboard = "static/new_dashboard.xlsx"

    print("Start upload test data.")
    count_documents = await get_count_documents_by_date_today()

    # TODO Написать проверку что все записи были записаны в БД
    #  а именно что count_documents == rows_in_xlsx (без учета шапки)
    if count_documents > 0:
        print(f"Documents found. Skipping loading test data. Count documents today:{count_documents}")
        return

    keys, rows = parse_xlsx(current_dashboard)
    converted_current_data = convert_xlsx_rows_to_dict(keys, rows)

    keys, rows = parse_xlsx(new_dashboard)
    converted_new_data = convert_xlsx_rows_to_dict(keys, rows)

    converted_data = merge_lines(converted_current_data, converted_new_data)

    await add_many_documents(converted_data)  # Множественная загрузка в БД
    print(f"Documents is uploaded. Count:{len(converted_data)}")
