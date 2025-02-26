# Модели данных (Models)

Модуль содержит Pydantic-модели для валидации и сериализации данных.

## Структура

```
models/
├── __init__.py         # Инициализация модуля
├── account.py          # Базовые модели аккаунтов
└── yandex_direct.py    # Модели для Яндекс.Директ
```

## Компоненты

### Базовые модели (account.py)

#### Account
Базовая модель аккаунта рекламной системы.

```python
class Account(BaseModel):
    account_name: str                           # Имя аккаунта
    source: str                                 # Тип источника
    auth: Union[YandexDirectAuth, VkAuth, dict] # Данные авторизации
```

#### Модели авторизации
```python
class YandexDirectAuth(BaseModel):
    login: str       # Логин в Яндекс.Директ
    token: str       # OAuth токен
    goals: list[int] # ID целей Метрики

class VkAuth(BaseModel):
    access_token: str # Токен доступа VK API
```

### Модели Яндекс.Директ (yandex_direct.py)

#### YandexDirectAccount
```python
class YandexDirectAccount(BaseModel):
    login: str       # Логин аккаунта
    token: str       # OAuth токен
    goals: list[int] # ID целей
```

#### YandexDirectBudget
```python
class YandexDirectBudget(BaseModel):
    budget: float    # Бюджет в рублях
```

#### YandexDirectStatistics
Модель для статистики рекламных кампаний.

```python
class YandexDirectStatistics(BaseModel):
    CampaignName: str | None  # Название кампании
    Age: str | None          # Возрастная группа
    Gender: str | None       # Пол
    Device: str | None       # Тип устройства
    Date: str | None        # Дата
    Impressions: int        # Показы
    Clicks: int            # Клики
    Cost: float           # Затраты
    Conversions: int      # Конверсии
    Sessions: int         # Сессии
    Bounces: int         # Отказы
```

### Особенности
- Автоматическая валидация данных через Pydantic
- Преобразование типов данных
- Документация полей через Field
- Примеры значений для API документации
- Автоматическая сериализация JSON
- Валидация зависимых полей
- Обработка пустых значений ("--") в статистике

### Пример использования

```python
from models.account import Account
from models.yandex_direct import YandexDirectStatistics

# Создание аккаунта
account = Account(
    account_name="Main Account",
    source="YANDEX_DIRECT",
    auth={
        "login": "your_login",
        "token": "your_token",
        "goals": [1, 2, 3]
    }
)

# Работа со статистикой
stats = YandexDirectStatistics(
    CampaignName="Test Campaign",
    Impressions="1000",  # Автоматически преобразуется в int
    Cost="150.50",      # Автоматически преобразуется в float
    Conversions_1="5",  # Будет учтено в общем количестве конверсий
    Conversions_2="3"   # Будет учтено в общем количестве конверсий
) 