from datetime import datetime, timedelta, time


def get_datetime_start_day(date: datetime = datetime.utcnow()) -> datetime:
    """Получение сегодняшней даты в формате datetime с минимальным значениями в часах."""
    return datetime.combine(date, time.min)


def get_datetime_for_last_week() -> datetime:
    return get_datetime_start_day() - timedelta(days=7)
