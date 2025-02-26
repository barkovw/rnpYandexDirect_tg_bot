import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)
os.chdir(root_dir)  # Меняем текущую директорию на корневую


import asyncio
import os
from database.db import init_db, add_account, get_all_accounts, update_account, delete_account

TEST_DB_PATH = "test_accounts.db"


async def test_init_db():
    print("\n=== Тестирование init_db ===")
    await init_db(TEST_DB_PATH)
    print("✓ База данных успешно инициализирована")


async def test_add_account():
    print("\n=== Тестирование add_account ===")
    # Добавляем тестовый аккаунт Яндекс.Директа
    await add_account(
        source="yandex_direct",
        account_name="test_account",
        auth={"login": "test_login", "token": "test_token", "goals": [1, 2, 3]},
        db_path=TEST_DB_PATH,
    )
    print("✓ Аккаунт Яндекс.Директа успешно добавлен")

    # Добавляем тестовый аккаунт VK
    await add_account(source="vk", auth={"token": "vk_test_token"}, db_path=TEST_DB_PATH)
    print("✓ Аккаунт VK успешно добавлен")


async def test_get_all_accounts():
    print("\n=== Тестирование get_all_accounts ===")
    accounts = await get_all_accounts(TEST_DB_PATH)
    print(f"Найдено аккаунтов: {len(accounts)}")
    for account in accounts:
        print(f"ID: {account['id']}, Источник: {account['source']}, Данные: {account['auth']}")
    assert len(accounts) == 2, "Должно быть два аккаунта"
    print("✓ Получение списка аккаунтов работает корректно")


async def test_update_account():
    print("\n=== Тестирование update_account ===")
    # Обновляем первый аккаунт
    await update_account(
        account_id=1,
        auth={"login": "updated_login", "token": "updated_token", "goals": [4, 5, 6]},
        db_path=TEST_DB_PATH,
    )
    accounts = await get_all_accounts(TEST_DB_PATH)
    updated_account = next(acc for acc in accounts if acc["id"] == 1)
    print(f"Обновленный аккаунт: {updated_account}")
    assert updated_account["auth"]["login"] == "updated_login"
    print("✓ Обновление аккаунта работает корректно")


async def test_delete_account():
    print("\n=== Тестирование delete_account ===")
    await delete_account(account_id=2, db_path=TEST_DB_PATH)
    accounts = await get_all_accounts(TEST_DB_PATH)
    assert len(accounts) == 1, "Должен остаться один аккаунт"
    print("✓ Удаление аккаунта работает корректно")


async def cleanup():
    print("\n=== Очистка тестовой среды ===")
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print("✓ Тестовая база данных удалена")


async def run_tests():
    try:
        await test_init_db()
        await test_add_account()
        await test_get_all_accounts()
        await test_update_account()
        await test_delete_account()
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(run_tests())
