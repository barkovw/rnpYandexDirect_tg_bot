import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)
os.chdir(root_dir)


import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)

from modules.yandex_direct.pandas_stat_proccessor import proccess_data


def test_proccess_data_with_grouping():
    test_data = [
        {'CampaignName': 'A', 'Impressions': 1000, 'Clicks': 100, 'Cost': 1000, 'Conversions': 0},
        {'CampaignName': 'A', 'Impressions': 2000, 'Clicks': 200, 'Cost': 2000, 'Conversions': 20},
        {'CampaignName': 'B', 'Impressions': 3000, 'Clicks': 300, 'Cost': 3000, 'Conversions': 30},
    ]
    
    result = proccess_data(test_data, group_by='Campaign')
    print(result)

def test_proccess_data_with_zero_values():
    test_data = [
        {'Impressions': 0, 'Clicks': 0, 'Cost': 0, 'Conversions': 0},
    ]
    
    result = proccess_data(test_data)
    print(result)

def run_tests():
    print("Запуск тестов pandas_stat_processor...")
    
    test_proccess_data_with_grouping()
    print("✓ Тест с группировкой пройден")
    
    test_proccess_data_with_zero_values()
    print("✓ Тест с нулевыми значениями пройден")
    
    print("Все тесты pandas_stat_processor пройдены успешно!")

if __name__ == "__main__":
    run_tests() 