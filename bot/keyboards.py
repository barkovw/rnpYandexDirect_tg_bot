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


def source_selection_keyboard(report_type: str, period: str = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора источника отчета
    
    :param report_type: Тип отчета (budgets, summary, etc.)
    :param period: Период для отчета (today, yesterday), если применимо
    :return: Клавиатура с кнопками источников
    """
    sources = [
        (Source.YANDEX_DIRECT.value, "Яндекс.Директ"),
    ]
    
    buttons = []
    for source_key, source_name in sources:
        callback_data = f"source_{report_type}_{source_key}"
        if period:
            callback_data = f"source_{report_type}_{period}_{source_key}"
        buttons.append([InlineKeyboardButton(text=source_name, callback_data=callback_data)])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def account_source_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора источника при добавлении аккаунта
    """
    sources = [
        (Source.YANDEX_DIRECT.value, "Яндекс.Директ"),
    ]
    
    buttons = []
    for source_key, source_name in sources:
        callback_data = f"select_source_{source_key}"
        buttons.append([InlineKeyboardButton(text=source_name, callback_data=callback_data)])
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def period_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора периода отчета (сегодня/вчера)
    """
    buttons = [
        [
            InlineKeyboardButton(text="За сегодня", callback_data="period_today"),
            InlineKeyboardButton(text="За вчера", callback_data="period_yesterday")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
