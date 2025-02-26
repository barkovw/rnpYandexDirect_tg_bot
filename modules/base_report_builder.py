from abc import ABC, abstractmethod
from typing import List, Dict, Any



class BaseReportBuilder(ABC):
    @abstractmethod
    async def fetch_budgets(self, accounts: List[Dict[str, Any]]) -> str:
        """Получает бюджеты для списка аккаунтов."""
        pass

    @abstractmethod
    async def fetch_summary_statistics(self, accounts: List[Dict[str, Any]], date_from: str, date_to: str) -> str:
        """Получает агрегированную статистику по всем аккаунтам за указанный период."""
        pass

    @abstractmethod
    async def fetch_detailed_statistics(self, accounts: List[Dict[str, Any]], date_from: str, date_to: str) -> List[str]:
        """Получает детальную статистику по каждому аккаунту за указанный период."""
        pass

