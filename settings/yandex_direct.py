from typing import List

ATTRIBUTION_MODEL: List[str] = "AUTO"
INCLUDE_VAT: bool = False
REPORT_TYPE: str = "CUSTOM_REPORT"
FILTERS: List[str] = []

REPORT_METRICS: List[str] = ["Impressions", "Clicks", "Cost", "Conversions", "Sessions", "Bounces"]

DETAIL_REPORT_DIMENSIONS: List[str] = ["CampaignName", "Age", "Gender", "Device", "Date"]

# Порог для предупреждения о низком бюджете (в рублях)
LOW_BUDGET_THRESHOLD: float = 3000.0

# Порог для предупреждения о высоком проценте отказов
HIGH_BOUNCE_RATE_THRESHOLD: float = 40.0

