import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env.local
load_dotenv(".env.local")

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)
os.chdir(root_dir)  # Меняем текущую директорию на корневую


import asyncio
import os
from datetime import datetime

from services.report_processor import ReportProcessor
from enums.sources import Source
from database.db import get_all_accounts, init_db, add_account, delete_account, drop_table


async def setup_test_db(db_path: str = "test_accounts.db"):
    """Создаем тестовую БД и наполняем тестовыми данными"""
    # Удаляем старую БД если она существует
    if os.path.exists(db_path):
        os.remove(db_path)

    # Инициализируем БД
    await init_db(db_path)

    # Отладочный вывод
    print("=== Переменные окружения ===")
    print(f"LOGIN: {os.getenv('YANDEX_DIRECT_LOGIN')}")
    print(f"TOKEN: {os.getenv('YANDEX_DIRECT_TOKEN')}")
    print(f"GOALS: {os.getenv('YANDEX_DIRECT_GOAL_IDS')}")
    print("==========================")

    test_accounts = []
    for i in range(1, 20):  # Создаем 10 аккаунтов
        test_accounts.append({
            "account_name": f"Тестовый аккаунт {i}",
            "auth": {
                "login": os.getenv("YANDEX_DIRECT_LOGIN"),
                "token": os.getenv("YANDEX_DIRECT_TOKEN"),
                "goals": [int(goal) for goal in os.getenv("YANDEX_DIRECT_GOAL_IDS", "").split(",") if goal],
            }
        })

    for account in test_accounts:
        await add_account("YANDEX_DIRECT", account["auth"], account["account_name"], db_path=db_path)

    return db_path


async def cleanup_db(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)


async def test_get_budgets_report():
    print("\n=== Тестируем получение бюджетов ===")
    db_path = await setup_test_db()

    try:
        processor = ReportProcessor(source=Source.YANDEX_DIRECT, db_path=db_path)
        result = await processor.get_budgets_report()

        # Проверяем что отчет это строка
        assert isinstance(result, str), "Результат должен быть строкой"
        print(result)

        print("✓ Тест получения бюджетов пройден")
    finally:
        await cleanup_db(db_path)


async def test_get_summary_report():
    print("\n=== Тестируем получение сводного отчета ===")
    db_path = await setup_test_db()

    try:
        processor = ReportProcessor(source=Source.YANDEX_DIRECT, db_path=db_path)
        result = await processor.get_summary_report()

        # Проверяем что отчет это строка
        assert isinstance(result, str), "Результат должен быть строкой"

        print(result)
        print("✓ Тест получения сводного отчета пройден")
    finally:
        await cleanup_db(db_path)


async def test_get_detailed_report():
    print("\n=== Тестируем получение детального отчета ===")
    db_path = await setup_test_db()

    try:
        processor = ReportProcessor(source=Source.YANDEX_DIRECT, db_path=db_path)
        accounts = await get_all_accounts(db_path)
        print("Тестовые аккаунты:")
        print(accounts)
        account_id = accounts[0]["id"]
        
        print(f"\nЗапрос детального отчета для аккаунта ID: {account_id}")
        result = await processor.get_detailed_report(account_id)
        
        # Проверяем что отчет это список строк
        assert isinstance(result, list), "Результат должен быть списком строк"
        
        for item in result:
            assert isinstance(item, str), "Каждый элемент результата должен быть строкой"
        
        print(f"\nПолучено отчетов: {len(result)}")
        
        print(result[0])

        if result[1]:
            print(result[1])


        print("✓ Тест получения детального отчета пройден")
    finally:
        await cleanup_db(db_path)


async def test_empty_db():
    print("\n=== Тестируем пустую БД ===")
    db_path = await setup_test_db()
    await drop_table(db_path)

    try:
        await init_db(db_path)
        processor = ReportProcessor(source=Source.YANDEX_DIRECT, db_path=db_path)

        budgets = await processor.get_budgets_report()
        summary = await processor.get_summary_report()

        accounts = await get_all_accounts(db_path)
        print(f"Аккаунты в БД: {accounts}")

        # Проверяем сообщения об отсутствии аккаунтов
        assert (
            "❌ *Нет аккаунтов для выбранного источника*" in budgets
        ), "Неверное сообщение для пустого отчета бюджетов"
        assert (
            "❌ *Нет аккаунтов для выбранного источника*" in summary
        ), "Неверное сообщение для пустого сводного отчета"

        print("✓ Тест пустой БД пройден")
    finally:
        await cleanup_db(db_path)


async def test_invalid_source():
    print("\n=== Тестируем неверный источник ===")
    db_path = await setup_test_db()

    try:
        with pytest.raises(ValueError) as exc_info:
            ReportProcessor(source="INVALID_SOURCE", db_path=db_path)
        assert "Неподдерживаемый источник данных" in str(exc_info.value)
        print("✓ Тест неверного источника пройден")
    finally:
        await cleanup_db(db_path)


async def test_account_preparation():
    print("\n=== Тестируем подготовку данных аккаунта ===")
    db_path = await setup_test_db()

    try:
        processor = ReportProcessor(source=Source.YANDEX_DIRECT, db_path=db_path)
        accounts = await get_all_accounts(db_path)

        prepared_accounts = processor.builder.prepare_accounts(accounts)
        assert len(prepared_accounts) == 1, "Должен быть 1 подготовленный аккаунт"

        prepared = prepared_accounts[0]
        assert prepared["login"] == os.getenv("YANDEX_DIRECT_LOGIN"), "Неверный логин"
        assert prepared["token"] == os.getenv("YANDEX_DIRECT_TOKEN"), "Неверный токен"
        assert prepared["goals"] == [int(goal) for goal in os.getenv("YANDEX_DIRECT_GOAL_IDS", "").split(",") if goal], "Неверные цели"

        print("✓ Тест подготовки данных аккаунта пройден")
    finally:
        await cleanup_db(db_path)


async def test_error_handling():
    print("\n=== Тестируем обработку ошибок ===")
    db_path = await setup_test_db()

    try:
        processor = ReportProcessor(source=Source.YANDEX_DIRECT, db_path=db_path)

        # Подменяем токен на неверный для проверки обработки ошибок
        accounts = await get_all_accounts(db_path)
        print(accounts)
        auth = accounts[0]["auth"]
        account_name = accounts[0]["account_name"]
        auth["token"] = "invalid_token"
        await delete_account(accounts[0]["id"], db_path)
        await add_account("YANDEX_DIRECT", auth, account_name, db_path=db_path)

        budgets = await processor.get_budgets_report()
        summary = await processor.get_summary_report()

        # Проверяем наличие сообщений об ошибках
        assert "❌" in budgets, "Отсутствует маркер ошибки в отчете бюджетов"
        assert "❌" in summary, "Отсутствует маркер ошибки в сводном отчете"

        print("✓ Тест обработки ошибок пройден")
    finally:
        await cleanup_db(db_path)


async def run_all_tests():
    print("Запуск всех тестов...")
    await test_get_budgets_report()
    await test_get_summary_report()
    #await test_get_detailed_report()
    # await test_empty_db()
    # await test_invalid_source()
    # await test_account_preparation()
    # await test_error_handling()
    print("\nВсе тесты завершены!")


if __name__ == "__main__":
    import pytest

    asyncio.run(run_all_tests())
