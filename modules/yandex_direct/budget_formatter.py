from typing import List, Union
from models.account import Account
from settings.yandex_direct import LOW_BUDGET_THRESHOLD

class BudgetFormatter:
    @staticmethod
    def format_budget_for_telegram(accounts: List[Account], budgets: List[Union[float, Exception]]) -> str:
        """
        Форматирует отчет о бюджетах для Telegram.
        
        :param accounts: Список аккаунтов
        :param budgets: Список бюджетов или ошибок
        :return: Отформатированная строка для Telegram
        """
        result = []
        
        for account, budget in zip(accounts, budgets):
            if isinstance(budget, Exception):
                error_text = str(budget).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[").replace("]", "\\]")
                result.append(f"*{account.account_name}* - ❌ `{error_text}`\n")
            else:
                emoji = "🔴" if budget.budget < LOW_BUDGET_THRESHOLD else ""
                result.append(f"*{account.account_name}* - `{budget.budget}` ₽ {emoji}\n")
            
        return "\n".join(result) 