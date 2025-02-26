from modules.base_report_builder import BaseReportBuilder
from modules.yandex_direct.yandex_direct_report_builder import YandexDirectReportBuilder
from enums.sources import Source


class ReportBuilderFactory:
    _builders = {
        Source.YANDEX_DIRECT: YandexDirectReportBuilder,
    }

    @classmethod
    def get_builder(cls, source: Source) -> BaseReportBuilder:
        builder_class = cls._builders.get(source)
        if not builder_class:
            raise ValueError(f"Неподдерживаемый источник данных: {source}")
        return builder_class()
