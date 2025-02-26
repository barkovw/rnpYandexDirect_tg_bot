# Модули отчетов (Modules)

Модуль содержит реализации построителей отчетов для различных рекламных систем.

## Структура

```
modules/
├── __init__.py                 # Инициализация модуля
├── base_report_builder.py      # Базовый класс построителя отчетов
├── report_builder_factory.py   # Фабрика построителей отчетов
└── yandex_direct/             # Модуль для Яндекс.Директ
    ├── budget_formatter.py           # Форматирование бюджетов
    ├── summary_statistics_formatter.py # Форматирование общей статистики
    ├── pandas_stat_proccessor.py     # Обработка статистики через pandas
    └── yandex_direct_report_builder.py # Построитель отчетов Яндекс.Директ
```

## Компоненты

### Базовый построитель (base_report_builder.py)

```python
class BaseReportBuilder(ABC):
    @abstractmethod
    async def fetch_budgets(self, accounts: List[Dict[str, Any]]) -> str:
        """Получает бюджеты для списка аккаунтов"""
        pass

    @abstractmethod
    async def fetch_summary_statistics(
        self, accounts: List[Dict[str, Any]], 
        date_from: str, 
        date_to: str
    ) -> str:
        """Получает агрегированную статистику"""
        pass

    @abstractmethod
    async def fetch_detailed_statistics(
        self, accounts: List[Dict[str, Any]], 
        date_from: str, 
        date_to: str
    ) -> List[str]:
        """Получает детальную статистику"""
        pass
```

### Фабрика построителей (report_builder_factory.py)

```python
class ReportBuilderFactory:
    _builders = {
        Source.YANDEX_DIRECT: YandexDirectReportBuilder,
        # Добавьте новые построители здесь
    }

    @classmethod
    def get_builder(cls, source: Source) -> BaseReportBuilder:
        return cls._builders[source]()
```

## Добавление нового рекламного источника

1. Создайте новую папку для источника:
```
modules/
└── new_source/                    # Папка нового источника
    ├── budget_formatter.py        # Форматирование бюджетов
    ├── statistics_formatter.py    # Форматирование статистики
    └── new_source_report_builder.py # Основной построитель
```

2. Реализуйте построитель отчетов:
```python
from modules.base_report_builder import BaseReportBuilder

class NewSourceReportBuilder(BaseReportBuilder):
    async def fetch_budgets(self, accounts):
        # Реализация получения бюджетов
        pass

    async def fetch_summary_statistics(self, accounts, date_from, date_to):
        # Реализация получения общей статистики
        pass

    async def fetch_detailed_statistics(self, accounts, date_from, date_to):
        # Реализация получения детальной статистики
        pass
```

3. Добавьте источник в `enums/sources.py`:
```python
class Source(Enum):
    YANDEX_DIRECT = "YANDEX_DIRECT"
    NEW_SOURCE = "NEW_SOURCE"  # Добавьте новый источник
```

4. Зарегистрируйте построитель в фабрике:
```python
class ReportBuilderFactory:
    _builders = {
        Source.YANDEX_DIRECT: YandexDirectReportBuilder,
        Source.NEW_SOURCE: NewSourceReportBuilder,  # Добавьте построитель
    }
```

5. Создайте модели в `models/`:
```python
class NewSourceAuth(BaseModel):
    # Определите поля авторизации
    pass

class NewSourceStatistics(BaseModel):
    # Определите поля статистики
    pass
```

6. Добавьте коннектор в `connectors/`:
```python
class NewSourceAPI:
    # Реализуйте методы работы с API
    pass
```

### Особенности
- Асинхронное выполнение операций
- Модульная архитектура
- Паттерн "Фабрика" для создания построителей
- Единый интерфейс через абстрактный класс
- Разделение форматирования и получения данных
- Поддержка pandas для обработки статистики 