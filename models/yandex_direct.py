from pydantic import BaseModel, Field, model_validator


class YandexDirectAccount(BaseModel):
    login: str = Field(..., description="Логин аккаунта Яндекс.Директ", example="svarka-test")
    token: str = Field(..., description="OAuth токен для доступа к API", example="3rwssrs3r3")
    goals: list[int] = Field(..., description="Цели аккаунта", example=[1, 2, 3])


class YandexDirectBudget(BaseModel):
    budget: float = Field(..., description="Бюджет аккаунта в рублях", example=10000.50)

from pydantic import BaseModel, Field, model_validator

class YandexDirectStatistics(BaseModel):
    CampaignName: str | None = None
    Age: str | None = None
    Gender: str | None = None
    Device: str | None = None
    Date: str | None = None
    Impressions: int = Field(default=0, description="Показы")
    Clicks: int = Field(default=0, description="Клики")
    Cost: float = Field(default=0.0, description="Затраты")
    Conversions: int = Field(default=0, description="Суммарные конверсии")
    Sessions: int = Field(default=0, description="Сессии")
    Bounces: int = Field(default=0, description="Отказы")

    @model_validator(mode="before")
    def pre_validation(cls, values: dict) -> dict:
        values = values.copy()

        # Преобразуем числовые поля, если они заданы корректно
        values["Impressions"] = int(values["Impressions"]) if values.get("Impressions") and values["Impressions"] != "--" else 0
        values["Clicks"] = int(values["Clicks"]) if values.get("Clicks") and values["Clicks"] != "--" else 0
        values["Cost"] = float(values["Cost"]) if values.get("Cost") and values["Cost"] != "--" else 0.0
        values["Sessions"] = int(values["Sessions"]) if values.get("Sessions") and values["Sessions"] != "--" else 0
        values["Bounces"] = int(values["Bounces"]) if values.get("Bounces") and values["Bounces"] != "--" else 0

        # Суммируем значения конверсий из полей с префиксом 'Conversions_'
        total_conversions = sum(
            int(v) if v != "--" else 0
            for k, v in values.items() if k.startswith("Conversions_")
        )
        # Удаляем отдельные поля конверсий
        values = {k: v for k, v in values.items() if not k.startswith("Conversions_")}
        values["Conversions"] = total_conversions

        return values
