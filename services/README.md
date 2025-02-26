# Сервисы (Services)

Модуль содержит бизнес-логику обработки отчетов и взаимодействия между компонентами системы.

## Структура

```
services/
└── report_processor.py  # Основной процессор отчетов
```

## Компоненты

### ReportProcessor (report_processor.py)

Основной класс для обработки отчетов различных рекламных систем.

```python
class ReportProcessor:
    def __init__(self, source: Source, db_path: str = "accounts.db"):
        self.source = source
        self.builder = ReportBuilderFactory.get_builder(source)
```

#### Основные методы

```python
# Получение отчета по бюджетам
async def get_budgets_report(self) -> str:
    """Возвращает отформатированный отчет по бюджетам всех аккаунтов"""

# Получение сводного отчета
async def get_summary_report(self) -> str:
    """Возвращает сводную статистику по всем аккаунтам"""

# Получение детального отчета
async def get_detailed_report(self, account_id: int) -> List[str]:
    """Возвращает детальную статистику по конкретному аккаунту"""
```

### Особенности
- Единая точка входа для получения отчетов
- Автоматическая фильтрация аккаунтов по источнику
- Обработка ошибок и пустых данных
- Автоматическое обновление дат из настроек
- Асинхронное выполнение операций

### Пример использования

```python
from services.report_processor import ReportProcessor
from enums.sources import Source

# Создание процессора для Яндекс.Директ
processor = ReportProcessor(source=Source.YANDEX_DIRECT)

# Получение отчета по бюджетам
budgets_report = await processor.get_budgets_report()
print(budgets_report)

# Получение сводной статистики
summary_report = await processor.get_summary_report()
print(summary_report)

# Получение детальной статистики по аккаунту
detailed_report = await processor.get_detailed_report(account_id=1)
for report_part in detailed_report:
    print(report_part)
```

### Добавление нового сервиса

1. Создайте новый файл сервиса:
```python
# services/new_service.py

class NewService:
    def __init__(self):
        # Инициализация зависимостей
        pass

    async def process_something(self):
        # Реализация бизнес-логики
        pass
```

2. Добавьте необходимые зависимости:
```python
from database.db import ...  # Доступ к БД
from models.something import ...  # Модели данных
from modules.something import ...  # Модули обработки
```

3. Следуйте принципам:
- Инкапсуляция бизнес-логики
- Асинхронное выполнение
- Обработка ошибок
- Логирование важных операций
- Минимальная связность с другими компонентами 