from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # встроено в Python 3.9+

MOSCOW_TZ = ZoneInfo("Europe/Moscow")

def get_date_from() -> str:
    """Возвращает дату начала периода (неделю назад) по московскому времени"""
    return (datetime.now(MOSCOW_TZ) - timedelta(days=7)).strftime("%Y-%m-%d")

def get_date_to() -> str:
    """Возвращает дату конца периода (сегодня) по московскому времени"""
    return datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d")

def get_default_date_range() -> tuple[str, str]:
    """Возвращает кортеж из двух дат (от, до) по московскому времени"""
    return get_date_from(), get_date_to()

def get_yesterday_date() -> str:
    """Возвращает вчерашнюю дату по московскому времени"""
    return (datetime.now(MOSCOW_TZ) - timedelta(days=1)).strftime("%Y-%m-%d")
