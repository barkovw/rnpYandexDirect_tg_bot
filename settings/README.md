# Настройки (Settings)

Модуль содержит конфигурационные параметры и настройки различных компонентов системы.

## Структура

```
settings/
├── __init__.py          # Инициализация модуля
├── bot.py              # Настройки Telegram бота
├── report_settings.py  # Настройки отчетов
└── yandex_direct.py   # Настройки Яндекс.Директ
```

## Компоненты


### Настройки Яндекс.Директ (yandex_direct.py)

Конфигурация для работы с API Яндекс.Директ:

```python
# Основные параметры отчетов
ATTRIBUTION_MODEL: List[str] = "AUTO"
INCLUDE_VAT: bool = False
REPORT_TYPE: str = "CUSTOM_REPORT"

# Метрики для отчетов
REPORT_METRICS: List[str] = [
    "Impressions", "Clicks", "Cost",
    "Conversions", "Sessions", "Bounces"
]

# Размерности для детальных отчетов
DETAIL_REPORT_DIMENSIONS: List[str] = [
    "CampaignName", "Age", "Gender",
    "Device", "Date"
]

# Пороговые значения
LOW_BUDGET_THRESHOLD: float = 3000.0      # Порог низкого бюджета
HIGH_BOUNCE_RATE_THRESHOLD: float = 40.0  # Порог высокого % отказов
```



### Настройки отчетов (report_settings.py)

Функции для работы с датами отчетов:

```python
def get_date_from() -> str:
    """Возвращает дату начала периода (неделю назад)"""
    return (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

def get_date_to() -> str:
    """Возвращает дату конца периода (сегодня)"""
    return datetime.now().strftime("%Y-%m-%d")

def get_default_date_range() -> tuple[str, str]:
    """Возвращает кортеж из двух дат (от, до)"""
    return get_date_from(), get_date_to()
```




### Особенности
- Централизованное управление настройками
- Типизированные конфигурационные параметры
- Удобные функции-помощники для дат
- Легкое добавление новых параметров
- Разделение настроек по компонентам
- Поддержка пороговых значений для мониторинга 