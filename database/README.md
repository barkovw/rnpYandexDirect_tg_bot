# База данных (Database)

Модуль для асинхронной работы с SQLite базой данных аккаунтов рекламных систем.

## Структура

```
database/
├── db.py         # Основной модуль работы с БД
```

## Основные компоненты

### База данных (accounts.db)

SQLite база данных с таблицей `accounts`:

| Поле         | Тип      | Описание                               |
|--------------|----------|----------------------------------------|
| id           | INTEGER  | Первичный ключ (автоинкремент)         |
| source       | TEXT     | Тип источника (yandex_direct, vk и др.)|
| auth         | TEXT     | JSON с данными аутентификации          |
| account_name | TEXT     | Имя аккаунта для идентификации        |

### Основные функции (db.py)

Все функции асинхронные, используют `aiosqlite`.

#### Инициализация
```python
async def init_db(db_path: str = "accounts.db") -> None
```
Создает БД и необходимые таблицы.

#### Управление аккаунтами

```python
# Добавление аккаунта
async def add_account(source: str, auth: dict, account_name: str = "") -> None

# Получение всех аккаунтов
async def get_all_accounts() -> list[dict]

# Получение аккаунта по ID
async def get_account_by_id(account_id: int) -> dict | None

# Обновление данных аккаунта
async def update_account(
    account_id: int,
    source: str = None,
    auth: dict = None,
    account_name: str = None
) -> None

# Удаление аккаунта
async def delete_account(account_id: int) -> None
```

### Особенности
- Асинхронное выполнение операций с БД
- Автоматическая сериализация/десериализация JSON для поля auth
- Валидация источников через enum
- Безопасное хранение учетных данных
- Поддержка именования аккаунтов для удобной идентификации

### Пример использования

```python
from database.db import init_db, add_account, get_all_accounts

# Инициализация БД
await init_db()

# Добавление аккаунта
await add_account(
    source="yandex_direct",
    auth={
        "login": "your_login",
        "token": "your_token"
    },
    account_name="Main Account"
)

# Получение всех аккаунтов
accounts = await get_all_accounts()
``` 