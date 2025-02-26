from datetime import datetime, timedelta

def get_date_from() -> str:
    """Возвращает дату начала периода (неделю назад)"""
    return (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

def get_date_to() -> str:
    """Возвращает дату конца периода (сегодня)"""
    return datetime.now().strftime("%Y-%m-%d")

def get_default_date_range() -> tuple[str, str]:
    """Возвращает кортеж из двух дат (от, до)"""
    return get_date_from(), get_date_to() 