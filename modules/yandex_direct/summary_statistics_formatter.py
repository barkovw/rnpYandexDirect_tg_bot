from typing import List, Union
import pandas as pd
from models.account import Account
from models.yandex_direct import YandexDirectStatistics
from modules.yandex_direct.pandas_stat_proccessor import proccess_data
from settings.yandex_direct import LOW_BUDGET_THRESHOLD

class SummaryStatisticsFormatter:
    @staticmethod
    def format_statistics_for_telegram(accounts: List[Account], statistics: List[Union[List[YandexDirectStatistics], Exception]], 
                                      budgets: List[Union[float, Exception]] = None) -> str:
        """
        Форматирует отчет о статистике для Telegram используя pandas для расчетов.
        
        :param accounts: Список аккаунтов
        :param statistics: Список статистики или ошибок для каждого аккаунта
        :param budgets: Список бюджетов или ошибок для каждого аккаунта
        :return: Отформатированная строка для Telegram
        """
        result = []
        
        for i, (account, stats) in enumerate(zip(accounts, statistics)):
            result.append(f"•*{account.account_name}*\n")
            
            # Показываем бюджет, если он доступен
            if budgets and i < len(budgets):
                budget = budgets[i]
                if isinstance(budget, Exception):
                    error_text = str(budget).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[").replace("]", "\\]")
                    result.append(f"Баланс: ❌ `{error_text}`\n")
                else:
                    emoji = "🔴" if budget.budget < LOW_BUDGET_THRESHOLD else ""
                    result.append(f"Баланс: `{budget.budget}` ₽ {emoji}\n")
            
            if isinstance(stats, Exception):
                error_text = str(stats).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[").replace("]", "\\]")
                result.append(f"❌ `{error_text}`\n")
            else:
                # Преобразуем статистику в список словарей
                data = [stat.model_dump() for stat in stats]
                
                # Если данных нет, создаем пустые данные
                if not data:
                    data = [{
                        'Impressions': 0,
                        'Clicks': 0,
                        'Cost': 0.0,
                        'Conversions': 0,
                        'Sessions': 0,
                        'Bounces': 0
                    }]
                
                # Используем proccess_data для обработки
                processed = proccess_data(data)
                totals = processed[0] if processed else {}
                
                # Форматируем вывод
                result.extend([
                    f"Показы: `{totals.get('Показы', 0)}`\n",
                    f"Клики: `{totals.get('Клики', 0)}`\n",
                    f"Расход: `{totals.get('Расход', 0)}` ₽\n",
                    f"Конверсии: `{totals.get('Конверсии', 0)}`\n",
                    f"Сессии: `{totals.get('Сессии', 0)}`\n",
                    f"Отказы: `{totals.get('Отказы', 0)}`\n",
                    f"Процент отказов: `{totals.get('Процент отказов', 0)}`%\n",
                    f"CTR: `{float(totals.get('CTR', 0))}`%\n",
                    f"CPC: `{float(totals.get('CPC', 0))}` ₽\n",
                    f"CR: `{float(totals.get('CR', 0))}`%\n",
                    f"CPA: `{float(totals.get('CPA', 0))}` ₽\n"
                ])
            
            result.append("\n")  # Разделитель между аккаунтами
            
        return "".join(result) 