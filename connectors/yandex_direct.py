import uuid
import asyncio
import aiohttp
from models.yandex_direct import YandexDirectBudget, YandexDirectStatistics


class YandexDirectAPI:
    SLEEP_TIME = 2

    def __init__(self, login: str, token: str):
        self._login = login
        self._token = token

    async def get_budgets(self, include_vat: bool) -> YandexDirectBudget:
        url = "https://api.direct.yandex.ru/live/v4/json/"
        payload = {
            "method": "AccountManagement",
            "token": self._token,
            "locale": "ru",
            "param": {"Action": "Get"},
        }
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    
                    
                    raise Exception(
                        f"Ошибка при получении бюджетов. Статус: {response.status}. Ответ сервера: {error_text}"
                    )
                data = await response.json()
                # Если API требует указания SelectionCriteria – добавляем его и повторяем запрос
                if data.get("error_detail") == "Поле SelectionCriteria должно быть указано" or (data.get("data", {}).get("Accounts", [{}])[0].get("Login") != self._login):
                    payload["param"]["SelectionCriteria"] = {"Logins": [self._login]}
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(
                                f"Ошибка при получении бюджетов. Статус: {response.status}. Ответ сервера: {error_text}"
                            )
                        data = await response.json()

        try:
            budget_value = float(data["data"]["Accounts"][0]["Amount"])
        except Exception:
            raise ValueError(
                "\nОшибка! \nОтвет сервера: \n" + str(data)
            )
        if include_vat:
            budget_value = round(budget_value * 1.2, 2)
        return YandexDirectBudget(budget=budget_value)

    async def get_statistics(
        self,
        date_from: str,
        date_to: str,
        goals: list[int],
        attribution_models: list[str],
        field_names: list[str],
        report_type: str,
        include_vat: bool,
    ) -> list[YandexDirectStatistics]:
        url = "https://api.direct.yandex.com/json/v5/reports"
        headers = {
            "Accept-Language": "ru",
            "processingMode": "auto",
            "returnMoneyInMicros": "false",
            "skipReportHeader": "true",
            "skipReportSummary": "true",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
            "Client-Login": self._login,
        }
        offset = 0
        all_data = []
        chunk_size = 50000
        report_name = str(uuid.uuid4())

        async with aiohttp.ClientSession() as session:
            while True:
                payload = {
                    "params": {
                        "SelectionCriteria": {"DateFrom": date_from, "DateTo": date_to},
                        "Goals": goals,
                        "AttributionModels": attribution_models,
                        "FieldNames": field_names,
                        "Page": {"Limit": chunk_size, "Offset": offset},
                        "ReportName": report_name,
                        "ReportType": report_type,
                        "DateRangeType": "CUSTOM_DATE",
                        "Format": "TSV",
                        "IncludeVAT": "YES" if include_vat else "NO",
                    }
                }
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        text = await response.text()
                        data_chunk = self._parse_tsv(text)
                        processed_chunk = [YandexDirectStatistics(**row) for row in data_chunk]
                        all_data.extend(processed_chunk)
                        if len(data_chunk) < chunk_size:
                            break
                        offset += chunk_size
                        report_name = str(uuid.uuid4())
                    elif response.status in [201, 202]:
                        print(f"Данные еще не готовы. Жду {self.SLEEP_TIME} секунд.")
                        await asyncio.sleep(self.SLEEP_TIME)
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"Ошибка при получении статистики. Статус: {response.status}. Ответ сервера: {error_text}"
                        )
        return all_data

    @staticmethod
    def _parse_tsv(tsv_data: str) -> list[dict]:
        lines = tsv_data.strip().split("\n")
        if not lines:
            return []
        headers = lines[0].split("\t")
        result = []
        for line in lines[1:]:
            values = line.split("\t")
            result.append(dict(zip(headers, values)))
        return result
