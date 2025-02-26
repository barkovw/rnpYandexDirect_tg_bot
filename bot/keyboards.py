from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enums.sources import Source


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Добавить аккаунт", callback_data="add_account")
    # builder.button(text="Массовое добавление", callback_data="bulk_add_accounts")
    builder.button(text="Список аккаунтов", callback_data="list_accounts")
    builder.button(text="Удалить аккаунт", callback_data="delete_account")
    builder.button(text="Бюджеты", callback_data="get_budgets")
    builder.button(text="Сводная статистика", callback_data="get_summary_report")
    builder.button(text="Детальная статистика", callback_data="get_detailed_report")
    builder.button(text="О боте", callback_data="about")

    builder.adjust(1)  # Размещаем кнопки в один столбец
    return builder.as_markup()


def source_selection_keyboard(report_type: str) -> InlineKeyboardMarkup:
    """
    report_type: "budgets", "summary" или "detailed"
    Формирует клавиатуру для выбора источника.
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text=Source.YANDEX_DIRECT.value, callback_data=f"source_{report_type}_YANDEX_DIRECT"
    )
    # Здесь можно добавить другие источники

    builder.adjust(1)
    return builder.as_markup()


def sources_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру из доступных источников в enum Sources
    """
    builder = InlineKeyboardBuilder()

    for source in Source:
        # Создаем человекочитаемое название
        display_name = source.value
        builder.button(text=display_name, callback_data=f"select_source_{source.value}")

    builder.adjust(1)  # Один столбец
    return builder.as_markup()
