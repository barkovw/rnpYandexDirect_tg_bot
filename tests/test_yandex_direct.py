import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)
os.chdir(root_dir)  # Меняем текущую директорию на корневую

import asyncio
from dotenv import load_dotenv
from connectors.yandex_direct import YandexDirectAPI
from settings.yandex_direct import INCLUDE_VAT, ATTRIBUTION_MODEL, DETAIL_REPORT_DIMENSIONS, REPORT_METRICS, REPORT_TYPE
from models.yandex_direct import YandexDirectBudget, YandexDirectStatistics


async def test_yd_budgets():
    load_dotenv(".env.local")

    token = os.getenv("YANDEX_DIRECT_TOKEN")
    login = os.getenv("YANDEX_DIRECT_LOGIN")
    
    if not token or not login:
        raise ValueError("Не заданы YANDEX_DIRECT_TOKEN или YANDEX_DIRECT_LOGIN в .env.local")

    api = YandexDirectAPI(login=login, token=token)
    
    try:
        # Тестируем получение бюджета без НДС
        budget_without_vat = await api.get_budgets(include_vat=False)
        print(f"Бюджет без НДС: {budget_without_vat.budget} руб.")
        
        # Тестируем получение бюджета с НДС
        budget_with_vat = await api.get_budgets(include_vat=True)
        print(f"Бюджет с НДС: {budget_with_vat.budget} руб.")
        
        print("Все тесты пройдены успешно!")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {str(e)}")
        raise


async def test_yd_statistics():
    load_dotenv(".env.local")

    token = os.getenv("YANDEX_DIRECT_TOKEN")
    login = os.getenv("YANDEX_DIRECT_LOGIN")
    goals = [int(goal) for goal in os.getenv("YANDEX_DIRECT_GOAL_IDS", "").split(",")]
    
    if not token or not login:
        raise ValueError("Не заданы YANDEX_DIRECT_TOKEN или YANDEX_DIRECT_LOGIN в .env.local")

    api = YandexDirectAPI(login=login, token=token)
    
    try:
        stats = await api.get_statistics(
            date_from="2024-01-31",
            date_to="2024-01-31",
            goals=goals,
            attribution_models=[ATTRIBUTION_MODEL],
            field_names=[*DETAIL_REPORT_DIMENSIONS, *REPORT_METRICS],
            report_type=REPORT_TYPE,
            include_vat=INCLUDE_VAT
        )
        print(stats[0])
        
            
        print("\nТест получения статистики пройден успешно!")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {str(e)}")
        raise


if __name__ == "__main__":
    #asyncio.run(test_yd_budgets())
    asyncio.run(test_yd_statistics())
