import os
from datetime import datetime, timedelta, time


def get_fake_datetime() -> datetime:
    """Получение даты с учетом сдвига по времени в зависимости от установленного значение в .env окружении."""
    return datetime.utcnow() + timedelta(days=int(os.environ.get('DAYS', 0)))


def get_datetime_start_day() -> datetime:
    """Получение сегодняшней даты в формате datetime с минимальным значениями в часах."""
    return datetime.combine(get_fake_datetime(), time.min)


def get_datetime_for_last_week() -> datetime:
    return get_datetime_start_day() - timedelta(days=7)
