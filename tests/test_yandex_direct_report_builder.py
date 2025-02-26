import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from connectors.yandex_direct import YandexDirectAPI
from settings.yandex_direct import INCLUDE_VAT, ATTRIBUTION_MODEL, DETAIL_REPORT_DIMENSIONS, REPORT_METRICS, REPORT_TYPE
from models.account import Account
from models.yandex_direct import YandexDirectAccount

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)
os.chdir(root_dir)

# Загружаем переменные окружения
load_dotenv(".env.local")

import pytest
import asyncio
from typing import List
from modules.yandex_direct.yandex_direct_report_builder import YandexDirectReportBuilder

# Тестовые данные конвертируем в модели Account
TEST_ACCOUNT_DATA = {
    "account_name": "Test Account",
    "source": "YANDEX_DIRECT",
    "auth": {
        "login": os.getenv("YANDEX_DIRECT_LOGIN"),
        "token": os.getenv("YANDEX_DIRECT_TOKEN"),
        "goals": [int(goal) for goal in os.getenv("YANDEX_DIRECT_GOAL_IDS", "").split(",")]
    }
}

SECOND_TEST_ACCOUNT_DATA = {
    "account_name": "Second Test Account",
    "source": "YANDEX_DIRECT",
    "auth": {
        "login": os.getenv("YANDEX_DIRECT_LOGIN"),
        "token": os.getenv("YANDEX_DIRECT_TOKEN"),
        "goals": [int(goal) for goal in os.getenv("YANDEX_DIRECT_GOAL_IDS", "").split(",")]
    }
}

class TestYandexDirectReportBuilder:
    def __init__(self):
        self.builder = YandexDirectReportBuilder()
        self.test_accounts = [
            Account(**TEST_ACCOUNT_DATA),
            Account(**SECOND_TEST_ACCOUNT_DATA)
        ]

    async def test_fetch_budgets(self):
        print("\n=== Тестируем получение бюджетов ===")
        
        # Тест успешного получения бюджетов
        budgets = await self.builder.fetch_budgets(self.test_accounts)
        print(budgets)
        assert isinstance(budgets, str), "Результат должен быть строкой"
        print("✓ Тест получения бюджетов пройден")

    async def test_fetch_summary_statistics(self):
        print("\n=== Тестируем получение сводной статистики ===")
        
        # Получаем статистику за последний день
        from datetime import datetime, timedelta
        today = datetime.now().date()
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            stats = await self.builder.fetch_summary_statistics(
                self.test_accounts,
                date_from=yesterday,
                date_to=yesterday
            )
            print("\nПолученная статистика:")
            print(stats)
            assert isinstance(stats, str), "Результат должен быть строкой"
            assert "*" in stats, "Результат должен содержать форматирование Markdown"
            assert "Показы:" in stats, "Результат должен содержать показы"
            assert "Клики:" in stats, "Результат должен содержать клики"
            assert "Расход:" in stats, "Результат должен содержать Расход"
            assert "Конверсии:" in stats, "Результат должен содержать конверсии"
            assert "Сессии:" in stats, "Результат должен содержать сессии"
            assert "Отказы:" in stats, "Результат должен содержать отказы"
            assert "Процент отказов:" in stats, "Результат должен содержать процент отказов"
            assert "CTR:" in stats, "Результат должен содержать CTR"
            assert "CPC:" in stats, "Результат должен содержать CPC"
            assert "CR:" in stats, "Результат должен содержать CR"
            assert "CPA:" in stats, "Результат должен содержать CPA"
            
            print("✓ Тест получения статистики пройден")
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {str(e)}")
            raise

    async def test_fetch_detailed_statistics(self):
        print("\n=== Тестируем получение детальной статистики ===")
        
        # Получаем статистику за последний день
        from datetime import datetime, timedelta
        today = datetime.now().date()
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            print(f"Запрос детальной статистики для аккаунта: {self.test_accounts[0].account_name}")
            print(f"Период: с {yesterday} по {yesterday}")
            
            stats = await self.builder.fetch_detailed_statistics(
                self.test_accounts[0],  # Тестируем на одном аккаунте
                date_from=yesterday,
                date_to=yesterday
            )
            
            print(f"\nПолучено отчетов: {len(stats)}")
            
            # Выводим только первый отчет и количество остальных для краткости
            if stats:
                print("\nПример первого отчета:")
                # Ограничиваем вывод первыми 10 строками для краткости
                first_report_lines = stats[0].split('\n')
                print('\n'.join(first_report_lines[:10]) + "\n... [сокращено для краткости]")
                
                if len(stats) > 1:
                    print(f"\nОстальные {len(stats) - 1} отчетов не выводятся для краткости")
            
            assert isinstance(stats, list), "Результат должен быть списком"
            assert len(stats) > 0, "Должен быть хотя бы один отчет"
            
            for report in stats:
                assert isinstance(report, str), "Каждый отчет должен быть строкой"
                assert "*" in report, "Результат должен содержать форматирование Markdown"
                assert "Показы:" in report, "Результат должен содержать показы"
                assert "Клики:" in report, "Результат должен содержать клики"
                assert "Расход:" in report, "Результат должен содержать Расход"
                assert "Конверсии:" in report, "Результат должен содержать конверсии"
            
            print("✓ Тест получения детальной статистики пройден")
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {str(e)}")
            raise

    async def test_fetch_detailed_statistics_with_invalid_data(self):
        print("\n=== Тестируем получение детальной статистики с некорректными данными ===")
        
        # Создаем тестовый аккаунт с неверным токеном
        invalid_account_data = {
            "account_name": "Invalid Test Account",
            "source": "YANDEX_DIRECT",
            "auth": {
                "login": "invalid_login",
                "token": "invalid_token",
                "goals": [123456]
            }
        }
        
        invalid_account = Account(**invalid_account_data)
        
        from datetime import datetime, timedelta
        today = datetime.now().date()
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            print(f"Запрос детальной статистики для невалидного аккаунта: {invalid_account.account_name}")
            print(f"Период: с {yesterday} по {yesterday}")
            
            stats = await self.builder.fetch_detailed_statistics(
                invalid_account,
                date_from=yesterday,
                date_to=yesterday
            )
            
            print(f"\nПолучено отчетов: {len(stats)}")
            
            if stats:
                print("\nСообщение об ошибке:")
                print(stats[0])
            
            assert isinstance(stats, list), "Результат должен быть списком"
            assert len(stats) == 1, "При ошибке должно быть только одно сообщение"
            
            error_report = stats[0]
            assert invalid_account.account_name in error_report, "Отчет должен содержать название аккаунта"
            assert "❌ Ошибка при получении статистики:" in error_report, "Отчет должен содержать сообщение об ошибке"
            assert "`" in error_report, "Текст ошибки должен быть в формате кода"
            
            print("✓ Тест получения детальной статистики с ошибками пройден")
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {str(e)}")
            raise

async def run_all_tests():
    print("Запуск тестов...")
    test_suite = TestYandexDirectReportBuilder()
    
    print("\nТест бюджетов:")
    await test_suite.test_fetch_budgets()
    
    print("\nТест статистики:")
    await test_suite.test_fetch_summary_statistics()
    
    # Добавляем флаг для выбора, какой тест запускать
    run_normal_test = True  # Установите в True для запуска обычного теста или False для теста с ошибками
    
    if run_normal_test:
        print("\nТест детальной статистики:")
        await test_suite.test_fetch_detailed_statistics()
    else:
        print("\nТест детальной статистики с ошибками:")
        await test_suite.test_fetch_detailed_statistics_with_invalid_data()
    
    print("\nВсе тесты завершены!")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 