import asyncio
from typing import List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from modules.base_report_builder import BaseReportBuilder
from connectors.yandex_direct import YandexDirectAPI
from settings.yandex_direct import INCLUDE_VAT, ATTRIBUTION_MODEL, REPORT_TYPE, REPORT_METRICS, DETAIL_REPORT_DIMENSIONS, LOW_BUDGET_THRESHOLD
from models.account import Account  # предполагается, что модель Account содержит нужные атрибуты
from modules.yandex_direct.budget_formatter import BudgetFormatter
from modules.yandex_direct.summary_statistics_formatter import SummaryStatisticsFormatter
from modules.yandex_direct.pandas_stat_proccessor import proccess_data

class YandexDirectReportBuilder(BaseReportBuilder):
    def __init__(self):
        super().__init__()
        # Семафор для ограничения одновременных запросов
        self.semaphore = asyncio.Semaphore(5)
        # Для контроля частоты запросов (20 запросов в течение 10 секунд)
        self.request_timestamps = []
        self.max_requests = 20
        self.window_seconds = 10

    async def _make_api_request(self, api_func, *args, **kwargs):
        # Контроль частоты запросов
        now = asyncio.get_event_loop().time()
        
        # Удаляем timestamp'ы старше окна в 10 секунд
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < self.window_seconds]
        
        # Если достигли лимита запросов в окне, нужно подождать
        if len(self.request_timestamps) >= self.max_requests:
            # Вычисляем, сколько нужно подождать
            oldest_timestamp = min(self.request_timestamps)
            wait_time = self.window_seconds - (now - oldest_timestamp)
            if wait_time > 0:
                print(f"Достигнут лимит запросов, ожидание {wait_time:.2f} секунд...")
                await asyncio.sleep(wait_time)
        
        # Добавляем текущий запрос в историю
        self.request_timestamps.append(asyncio.get_event_loop().time())
        
        # Выполняем запрос через семафор как обычно
        async with self.semaphore:
            return await api_func(*args, **kwargs)

    async def fetch_budgets(self, accounts: List[Account]) -> str:
        tasks = []
        for account in accounts:
            api = YandexDirectAPI(account.auth.login, account.auth.token)
            tasks.append(self._make_api_request(api.get_budgets, INCLUDE_VAT))
            
        budgets = await asyncio.gather(*tasks, return_exceptions=True)
        print(budgets)
        return BudgetFormatter.format_budget_for_telegram(accounts, budgets)
    
    async def fetch_summary_statistics(self, accounts: List[Account], date_from: str, date_to: str) -> str:
        statistics_tasks = []
        budget_tasks = []
        
        for account in accounts:
            auth = account.auth
            api = YandexDirectAPI(auth.login, auth.token)
            
            # Задачи для статистики
            params = {
                "date_from": date_from,
                "date_to": date_to,
                "goals": auth.goals,
                "attribution_models": [ATTRIBUTION_MODEL],
                "field_names": REPORT_METRICS,
                "report_type": REPORT_TYPE,
                "include_vat": INCLUDE_VAT,
            }
            statistics_tasks.append(self._make_api_request(api.get_statistics, **params))
            
            # Задачи для бюджетов
            budget_tasks.append(self._make_api_request(api.get_budgets, INCLUDE_VAT))

        # Выполняем все задачи параллельно
        statistics_results = await asyncio.gather(*statistics_tasks, return_exceptions=True)
        budget_results = await asyncio.gather(*budget_tasks, return_exceptions=True)
        
        return SummaryStatisticsFormatter.format_statistics_for_telegram(accounts, statistics_results, budget_results)


    async def fetch_detailed_statistics(self, account: Account, date_from: str, date_to: str) -> List[str]:
        reports = []
        auth = account.auth
        api = YandexDirectAPI(auth.login, auth.token)

        # Словарь для перевода названий полей
        dimension_to_russian = {
            'CampaignName': 'Название кампании',
            'Age': 'Возраст',
            'Gender': 'Пол',
            'Device': 'Устройство',
            'Date': 'Дата'
        }

        try:
            # Подготавливаем все задачи для параллельного выполнения
            tasks = []
            
            # Задача для получения бюджета и общей статистики
            budget_params = {"include_vat": INCLUDE_VAT}
            summary_params = {
                "date_from": date_from,
                "date_to": date_to,
                "goals": auth.goals,
                "attribution_models": [ATTRIBUTION_MODEL],
                "field_names": REPORT_METRICS,
                "report_type": REPORT_TYPE,
                "include_vat": INCLUDE_VAT,
            }

            logger.info("Запуск запросов к API для бюджета и общей статистики")
            budget_data, summary_stats = await asyncio.gather(
                self._make_api_request(api.get_budgets, **budget_params),
                self._make_api_request(api.get_statistics, **summary_params),
                return_exceptions=True
            )
            
            # Обрабатываем результат получения бюджета
            balance = "Не доступно"
            if isinstance(budget_data, Exception):
                logger.error(f"Ошибка при получении бюджета: {budget_data}")
            elif budget_data and hasattr(budget_data, 'budget'):
                balance = budget_data.budget
                logger.info(f"Получен баланс: {balance}")
            
            # Формируем общую сводку
            summary_report = [f"*{account.account_name}*\n\n"]
            summary_report.append(f"Остаток на балансе: `{balance}` ₽\n\n")
            summary_report.append("*Общая сводка*\n\n")
            
            # Обрабатываем результат получения общей статистики
            if isinstance(summary_stats, Exception):
                logger.error(f"Ошибка при получении общей статистики: {summary_stats}")
                error_text = str(summary_stats).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[").replace("]", "\\]")
                summary_report.append(f"❌ Ошибка при получении общей статистики: `{error_text}`\n\n")
                # Если ошибка в общей статистике, сразу возвращаем отчет с ошибкой
                return ["".join(summary_report)]
            elif summary_stats:
                # Преобразуем общую статистику в список словарей
                summary_data = [stat.model_dump() for stat in summary_stats]
                
                # Обрабатываем данные без группировки
                summary_processed = proccess_data(summary_data)
                
                if summary_processed:
                    row = summary_processed[0]  # Берем первую (и единственную) строку с общей статистикой
                    
                    summary_report.extend([
                        f"Показы: `{row.get('Показы', 0)}`\n",
                        f"Клики: `{row.get('Клики', 0)}`\n",
                        f"Расход: `{row.get('Расход', 0)}` ₽\n",
                        f"Конверсии: `{row.get('Конверсии', 0)}`\n",
                        f"Сессии: `{row.get('Сессии', 0)}`\n",
                        f"Отказы: `{row.get('Отказы', 0)}`\n",
                        f"Процент отказов: `{row.get('Процент отказов', 0)}`%\n",
                        f"CTR: `{float(row.get('CTR', 0))}`%\n",
                        f"CPC: `{float(row.get('CPC', 0))}` ₽\n",
                        f"CR: `{float(row.get('CR', 0))}`%\n",
                        f"CPA: `{float(row.get('CPA', 0))}` ₽\n\n"
                    ])
            else:
                summary_report.append("❌ Нет данных за указанный период\n\n")
            
            # Добавляем общую сводку в начало списка отчетов
            reports.append("".join(summary_report))
            
            # Задачи для получения детальной статистики по каждому измерению
            dimension_tasks = []
            for dimension in DETAIL_REPORT_DIMENSIONS:
                params = {
                    "date_from": date_from,
                    "date_to": date_to,
                    "goals": auth.goals,
                    "attribution_models": [ATTRIBUTION_MODEL],
                    "field_names": [dimension, *REPORT_METRICS],
                    "report_type": REPORT_TYPE,
                    "include_vat": INCLUDE_VAT,
                }
                dimension_tasks.append((dimension, self._make_api_request(api.get_statistics, **params)))
            
            # Выполняем все задачи для измерений параллельно
            dimension_results = []
            for dimension, task in dimension_tasks:
                try:
                    stats = await task
                    dimension_results.append((dimension, stats))
                except Exception as e:
                    logger.error(f"Ошибка при получении статистики для {dimension}: {e}")
                    error_text = str(e).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[").replace("]", "\\]")
                    reports.append(f"❌ Ошибка при получении статистики для {dimension_to_russian[dimension]}: `{error_text}`\n")
            
            # Обрабатываем результаты по измерениям
            for dimension, stats in dimension_results:
                if not stats:
                    reports.append(f"❌ Нет данных за указанный период для {dimension_to_russian[dimension]}\n")
                    continue
                
                # Преобразуем статистику в список словарей
                data = [stat.model_dump() for stat in stats]
                
                # Обрабатываем данные с группировкой
                processed = proccess_data(data, group_by=dimension)
                
                # Формируем отчет для текущей группировки
                report = []
                
                # Добавляем заголовок группировки
                report.append(f"Отчет по параметру: _{dimension_to_russian[dimension]}_\n\n")
                
                for row in processed:
                    # Получаем значение группировки по русскому названию поля
                    dimension_value = row.get(dimension_to_russian[dimension], 'Не указано')
                    
                    report.append(f"*{dimension_value}*\n")
                    report.extend([
                        f"Показы: `{row.get('Показы', 0)}`\n",
                        f"Клики: `{row.get('Клики', 0)}`\n",
                        f"Расход: `{row.get('Расход', 0)}` ₽\n",
                        f"Конверсии: `{row.get('Конверсии', 0)}`\n",
                        f"Сессии: `{row.get('Сессии', 0)}`\n",
                        f"Отказы: `{row.get('Отказы', 0)}`\n",
                        f"Процент отказов: `{row.get('Процент отказов', 0)}`%\n",
                        f"CTR: `{float(row.get('CTR', 0))}`%\n",
                        f"CPC: `{float(row.get('CPC', 0))}` ₽\n",
                        f"CR: `{float(row.get('CR', 0))}`%\n",
                        f"CPA: `{float(row.get('CPA', 0))}` ₽\n\n"
                    ])
                
                reports.append("".join(report))
                
        except Exception as e:
            # В случае ошибки возвращаем один отчет с информацией об ошибке
            error_text = str(e).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[").replace("]", "\\]")
            error_message = f"*{account.account_name}*\n\n❌ `{error_text}`"
            return [error_message]
        
        return reports

