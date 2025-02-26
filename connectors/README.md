# Коннекторы (Connectors)

Модуль содержит коннекторы к различным рекламным системам для асинхронного получения данных.

## Структура

```
connectors/
├── __init__.py          # Инициализация модуля
└── yandex_direct.py     # Коннектор к Яндекс.Директ API
```

## Яндекс.Директ API (yandex_direct.py)

### Класс YandexDirectAPI

Асинхронный клиент для работы с API Яндекс.Директ v4/v5.

#### Инициализация

```python
client = YandexDirectAPI(login="your_login", token="your_oauth_token")
```

#### Методы

##### get_budgets
```python
async def get_budgets(include_vat: bool) -> YandexDirectBudget
```
Получает текущий баланс аккаунта.

**Параметры:**
- `include_vat`: bool - включать ли НДС (20%) в возвращаемую сумму

**Возвращает:**
- `YandexDirectBudget` с полем `budget` (float)

##### get_statistics
```python
async def get_statistics(
    date_from: str,
    date_to: str,
    goals: list[int],
    attribution_models: list[str],
    field_names: list[str],
    report_type: str,
    include_vat: bool
) -> list[YandexDirectStatistics]
```
Получает статистику по заданным параметрам.

**Параметры:**
- `date_from`: str - начальная дата в формате "YYYY-MM-DD"
- `date_to`: str - конечная дата в формате "YYYY-MM-DD"
- `goals`: list[int] - список ID целей
- `attribution_models`: list[str] - модели атрибуции
- `field_names`: list[str] - запрашиваемые поля статистики
- `report_type`: str - тип отчета
- `include_vat`: bool - включать ли НДС в денежные показатели

**Возвращает:**
- Список объектов `YandexDirectStatistics`

### Особенности
- Асинхронное выполнение запросов (asyncio + aiohttp)
- Автоматическая пагинация для больших отчетов
- Обработка ошибок и повторные попытки
- Поддержка TSV формата ответов
- Автоматический учет НДС
