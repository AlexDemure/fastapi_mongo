from decimal import Decimal, ROUND_DOWN
from typing import Union

from openpyxl import load_workbook

from backend.src.apps.xlsx.serializer import prepare_current_data_to_mongo, prepare_new_data_to_mongo


def parse_xlsx(filepath: str) -> tuple:
    """
    Функция для парсинга данных из xlsx файла.

    Возвращает ключи с названием столбцом таблицы и их значениями в виде строк.
    Данная функция должна быть в репозитории где скачивается файл со статистикой.
    """
    rows = []  # Данные книг
    keys = []  # Шапка документа с названием столбцом.

    file = load_workbook(filename=filepath)  # Открытие документа
    sheet = file.active  # Выбор активного листа

    for index, row in enumerate(sheet.rows):
        if index == 0:
            keys = [x.value for x in row]
            continue

        # Преобразуем данные внутри строки в список
        rows.append([x.value for x in row])

    return keys, rows


def convert_xlsx_rows_to_dict(keys: list, rows: list) -> list:
    """
    Преобразование XLSX данных в словари.

    На выходе получаем список словарей в формате [{isbn: ..., hours: ..., author: ...}, {}, {}]
    Данная функция должна быть в репозитории где скачивается файл со статистикой.
    """
    converted_data = []  # Готовая дата

    for row in rows:
        row_to_dict = {}  # Строка XLSX преобразованная в словарь

        # Перебор значений в строке XLSX и присваивание ключа к значению по номеру индекса из списка ключей.
        for index, item in enumerate(row):
            row_to_dict[keys[index]] = item

        converted_data.append(row_to_dict)

    return converted_data


def merge_lines(current_dashboard: list, new_dashboard: list) -> list:
    """
    Функция для слияния двух строк из разных таблицы XLSX необходимо для подготовки данных в MongoDB.

    Данная функция должна быть в репозитории где скачивается файл со статистикой.
    """

    merged_items = []

    for dict_current_data in current_dashboard:
        for key, value in dict_current_data.items():  # Перебор ключей в строке основонго дашборда
            if key == "Title":  # Если ключ Title начинаем поиск по названию внутри нового дашборда

                row_is_find = False  # Начальное состояние поиска

                for dict_new_data in new_dashboard:  # Перебор ключей в строке основонго дашборда

                    if value == dict_new_data['Title']:  # Если значения совпадают собираем все в одну строку.
                        data = {
                            **prepare_current_data_to_mongo(dict_current_data),
                            **prepare_new_data_to_mongo(dict_new_data),
                        }

                        merged_items.append(data)

                        new_dashboard.remove(dict_new_data)  # Удаляем из нового дашборда найденный результат.

                        row_is_find = True  # Переключаем состояние что строка найдена и выходим из дальнейшего поиска.
                        break

                if row_is_find is False:  # Иначе заполняем дефолтными значениями из нового дашборда
                    data = {
                        **prepare_current_data_to_mongo(dict_current_data),
                        **prepare_new_data_to_mongo(),
                    }
                    merged_items.append(data)

    return merged_items
