import asyncio
import inspect
import threading
from decimal import Decimal, ROUND_DOWN
from typing import Union

from backend.src.core.config import settings
from backend.src.db.database import AIOMotor


def convert_number_to_decimal(num: Union[int, float, Decimal]) -> Decimal:
    """
    Конвертация всех числовых значений в Decimal с округлением вниз.

    На выходе получаем Decimal в формате 0.00
    """
    return Decimal(num).quantize(Decimal('0.00'), rounding=ROUND_DOWN)


def async_function_wrapper_to_run_in_thread(async_func, args=None):
    """
    Обертка для асинхронной функции, чтобы запустить ее в отдеьном потоке.

    Обертка передается в объект Thread модуля threading в качестве цели для выполнения.
    Оберктка необходима, т.к. метод run_in_executor модул asyncio работает только с синхронными,
    (блокирующими event loop) функциями.
    :param async_func: Асинхронная функция
    :param args: Аргументы, которые необходимо передать в асинхронную функцию.
    """

    loop = asyncio.new_event_loop()  # Создаем новый event_loop
    asyncio.set_event_loop(loop)  # Устанавливаем event_loop ак текущий для нового поток

    db = AIOMotor("dashboards", "statistics", settings.get_uri())
    db.init_connection()  # Инициализируем новое соединение к MongoDB в потоке

    if args is None:
        loop.run_until_complete(async_func(db))
    else:
        loop.run_until_complete(async_func(args, db))

    loop.close()


def run_function_in_separate_thread(func, args=None):
    """
    Запускает функцию в потоке отдельном от основного.

    Синхронную (блокирующую event loop) функцию лучше запускать через метод
    run_in_executor модуля asyncio, а данный метод использовать,
    если невозможно использование run_in_executor.
    :param func: Функция, которая должна быть запущена в отдельном потоке.
    :param args: Аргументы, которые необходимо передать в запускаемую функцию.
    """
    if inspect.iscoroutinefunction(func):  # Проверяем, является ли функци асинхронной.
        new_thread = threading.Thread(
            target=async_function_wrapper_to_run_in_thread,  # Обертка для запуска асинхронной функции в отд. потоке
            args=(func, args)
        )
    else:  # Если функция вляется синхронной
        new_thread = threading.Thread(
            target=func,
            args=(args, )
        )
    new_thread.start()  # Запускаем новый поток
