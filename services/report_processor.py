import asyncio
from typing import List, Dict, Any, Optional
from enums.sources import Source
from database.db import get_all_accounts, get_account_by_id
from modules.report_builder_factory import ReportBuilderFactory
from modules.base_report_builder import BaseReportBuilder
from models.account import Account
from settings.report_settings import get_date_from, get_date_to

class ReportProcessor:
    def __init__(self, source: Source, db_path: str = "accounts.db"):
        """
        :param source: Источник данных из enum Source
        :param db_path: Путь к базе данных с аккаунтами
        """
        self.source = source
        self.db_path = db_path
        self.builder: BaseReportBuilder = ReportBuilderFactory.get_builder(source)
        self._update_dates()

    def _update_dates(self) -> None:
        """Обновляет даты из настроек"""
        self.date_from = get_date_from()
        self.date_to = get_date_to()
        print(self.date_from, self.date_to)

    async def _get_filtered_accounts(self) -> List[Account]:
        raw_accounts = await get_all_accounts(self.db_path)
        accounts = [Account(**acc) for acc in raw_accounts]
        filtered_accounts = [
            acc for acc in accounts if Source(acc.source.upper()) == self.source
        ]
        return filtered_accounts

    async def _process_report(self, report_func, *args) -> Any:
        accounts = await self._get_filtered_accounts()
        if not accounts:
            return "❌ *Нет аккаунтов для выбранного источника*"
        return await report_func(accounts, *args)

    async def get_budgets_report(self) -> str:
        return await self._process_report(self.builder.fetch_budgets)

    async def get_summary_report(self) -> str:
        self._update_dates()
        return await self._process_report(
            self.builder.fetch_summary_statistics, 
            self.date_to, 
            self.date_to
        )

    async def get_detailed_report(self, account_id: int) -> List[str]:
        """
        Получает детальный отчет для конкретного аккаунта.
        
        :param account_id: ID аккаунта для получения статистики
        :return: Список строк с отчетом
        """
        self._update_dates()
        account_dict = await get_account_by_id(account_id, db_path=self.db_path)
        if not account_dict:
            return ["❌ *Аккаунт не найден*"]
        
        # Преобразуем словарь в объект Account
        account = Account(**account_dict)
        
        return await self.builder.fetch_detailed_statistics(account, self.date_from, self.date_to)
