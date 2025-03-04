import json
from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ErrorEvent, BotCommand, BotCommandScopeDefault
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

from database.db import add_account, delete_account, get_all_accounts, get_account_by_id
from enums.sources import Source
from services.report_processor import ReportProcessor
from bot.keyboards import main_menu_keyboard, source_selection_keyboard, source_selection_keyboard, period_selection_keyboard, account_source_selection_keyboard

# Создаем роутер для регистрации хендлеров
router = Router()

# Регистрация команд бота
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="menu", description="Открыть главное меню")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

# Состояния для добавления одного аккаунта
class AddAccountStates(StatesGroup):
    waiting_for_source = State()  # Сначала выбор источника
    waiting_for_name = State()    # Потом название аккаунта
    waiting_for_credentials = State()  # Потом логин;токен;цели


# Состояния для массового добавления аккаунтов
class BulkAddAccountStates(StatesGroup):
    waiting_for_bulk_data = State()


# Состояния для удаления аккаунта
class DeleteAccountStates(StatesGroup):
    waiting_for_account_id = State()


# Состояния для получения детальной статистики
class DetailedReportStates(StatesGroup):
    waiting_for_account_id = State()


# Обновляем хендлеры
@router.message(Command("start", "menu"))
async def menu_command(message: Message):
    await message.answer("Выберите действие:", reply_markup=main_menu_keyboard())


# --- Добавление аккаунта ---
@router.callback_query(F.data == "add_account")
async def add_account_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Выберите источник:", reply_markup=account_source_selection_keyboard())
    await state.set_state(AddAccountStates.waiting_for_source)
    await callback.answer()


@router.callback_query(AddAccountStates.waiting_for_source, F.data.startswith("select_source_"))
async def process_source_selection(callback: CallbackQuery, state: FSMContext):
    # Получаем полное значение источника
    source = callback.data.replace("select_source_", "")
    await state.update_data(source=source.upper())  # Сохраняем в верхнем регистре
    await callback.message.answer("Введите название аккаунта (для удобства идентификации):")
    await state.set_state(AddAccountStates.waiting_for_name)
    await callback.answer()


@router.message(AddAccountStates.waiting_for_name)
async def process_account_name(message: Message, state: FSMContext):
    account_name = message.text.strip()
    await state.update_data(account_name=account_name)
    await message.answer(
        "Введите данные в формате: логин;токен;цели\n"
        "Например: my-account;y0_token123;123,456,789\n"
        "Где цели указываются через запятую"
    )
    await state.set_state(AddAccountStates.waiting_for_credentials)


@router.message(AddAccountStates.waiting_for_credentials)
async def process_credentials(message: Message, state: FSMContext):
    try:
        # Разбираем строку с данными
        login, token, goals_str = message.text.strip().split(";")

        # Обрабатываем цели
        try:
            goals = [int(g.strip()) for g in goals_str.split(",") if g.strip()]
        except ValueError:
            await message.answer(
                "Ошибка: цели должны быть числами, разделенными запятой. Попробуйте снова:"
            )
            return

        # Получаем сохраненные данные
        data = await state.get_data()
        source = data.get("source")
        account_name = data.get("account_name")

        # Создаем данные аккаунта
        auth = {"login": login.strip(), "token": token.strip(), "goals": goals}

        # Добавляем аккаунт, используя значение из enum
        await add_account(source=Source(source).value, auth=auth, account_name=account_name)
        await message.answer(
            f"Аккаунт {account_name} успешно добавлен!", reply_markup=main_menu_keyboard()
        )
        await state.clear()

    except ValueError as e:
        if "Неподдерживаемый источник" in str(e):
            await message.answer(str(e))
        else:
            await message.answer("Ошибка при добавлении аккаунта:\n" "текст ошибки: " + str(e))
        return


# --- Просмотр списка аккаунтов ---
@router.callback_query(F.data == "list_accounts")
async def list_accounts(callback: CallbackQuery):
    accounts = await get_all_accounts()
    if not accounts:
        await callback.message.answer("Список аккаунтов пуст", reply_markup=main_menu_keyboard())
        await callback.answer()
        return

    text = "📋 *Список аккаунтов:*\n\n"
    for acc in accounts:
        # Экранируем нижние подчеркивания в названии источника
        source = acc['source'].replace("_", "\\_")
        text += (
            f"ID: `{acc['id']}`\n"
            f"Название: {acc['account_name']}\n"
            f"Источник: {source}\n"
            f"\n"
        )

    # Разбиваем на части, если сообщение слишком длинное
    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            chunk = text[x : x + 4096]
            await callback.message.answer(chunk, parse_mode="Markdown")
    else:
        await callback.message.answer(text, parse_mode="Markdown")

    await callback.message.answer("Выберите действие:", reply_markup=main_menu_keyboard())
    await callback.answer()


# --- Массовое добавление аккаунтов ---
@router.callback_query(F.data == "bulk_add_accounts")
async def bulk_add_account_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Отправьте данные для массового добавления аккаунтов в формате JSON.\n"
        "Пример:\n"
        '[{"source": "yandex_direct", "auth": {"login": "user1", "token": "token1", "goals": [1,2,3]}}, ...]'
    )
    await state.set_state(BulkAddAccountStates.waiting_for_bulk_data)
    await callback.answer()


@router.message(BulkAddAccountStates.waiting_for_bulk_data)
async def bulk_add_account_receive(message: Message, state: FSMContext):
    try:
        accounts = json.loads(message.text)
        if not isinstance(accounts, list):
            raise ValueError("Ожидался список аккаунтов")
        for acc in accounts:
            source = acc.get("source")
            auth = acc.get("auth")
            if not source or not auth:
                continue
            await add_account(source=source.lower(), auth=auth)
        await message.answer("Массовое добавление завершено!", reply_markup=main_menu_keyboard())
    except Exception as e:
        await message.answer(f"Ошибка при разборе данных: {e}")
    await state.clear()


# --- Удаление аккаунта ---
@router.callback_query(F.data == "delete_account")
async def delete_account_start(callback: CallbackQuery, state: FSMContext):
    accounts = await get_all_accounts()
    if not accounts:
        await callback.message.answer(
            "Нет аккаунтов для удаления.", reply_markup=main_menu_keyboard()
        )
        await callback.answer()
        return
    
    await callback.message.answer("Введите ID аккаунта для удаления:")
    await state.set_state(DeleteAccountStates.waiting_for_account_id)
    await callback.answer()


@router.message(DeleteAccountStates.waiting_for_account_id)
async def delete_account_receive(message: Message, state: FSMContext):
    try:
        account_id = int(message.text.strip())
        await delete_account(account_id)
        await message.answer(
            f"Аккаунт с ID {account_id} удалён.", reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        await message.answer(f"Ошибка при удалении: {e}")
    await state.clear()


# --- Получение бюджетов ---
@router.callback_query(F.data == "get_budgets")
async def get_budgets(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите источник для получения бюджетов:",
        reply_markup=source_selection_keyboard(report_type="budgets"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("source_budgets_"))
async def get_budgets_source(callback: CallbackQuery):
    source = callback.data.replace("source_budgets_", "")
    
    # Отправляем промежуточное сообщение
    progress_message = await callback.message.answer("⏳ *Готовлю отчет по бюджетам...*", parse_mode="Markdown")
    await callback.answer()
    
    try:
        processor = ReportProcessor(source=Source(source), db_path="accounts.db")
        report = await processor.get_budgets_report()
        
        # Удаляем промежуточное сообщение
        await progress_message.delete()
        
        await callback.message.answer(report, parse_mode="Markdown")
    except Exception as e:
        error_text = str(e).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[").replace("]", "\\]")
        await progress_message.edit_text(f"❌ *Ошибка при подготовке отчета:*\n{error_text}", parse_mode="Markdown")


# --- Получение сводной статистики ---
@router.callback_query(F.data == "get_summary_report")
async def get_summary_report(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите период для получения сводной статистики:",
        reply_markup=period_selection_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("period_"))
async def process_period_selection(callback: CallbackQuery, state: FSMContext):
    period = callback.data.replace("period_", "")
    
    # Сохраняем выбранный период в состоянии
    await state.update_data(selected_period=period)
    
    await callback.message.answer(
        f"Выберите источник для получения сводной статистики за {'сегодня' if period == 'today' else 'вчера'}:",
        reply_markup=source_selection_keyboard(report_type="summary", period=period),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("source_summary_"))
async def get_summary_report_source(callback: CallbackQuery, state: FSMContext):
    callback_data = callback.data.replace("source_summary_", "")
    
    # Проверяем, содержит ли callback данные о периоде
    if "_" in callback_data:
        period, source = callback_data.split("_", 1)
    else:
        # Обратная совместимость со старым форматом
        source = callback_data
        # Получаем период из состояния
        user_data = await state.get_data()
        period = user_data.get("selected_period", "today")  # По умолчанию - сегодня
    
    # Отправляем промежуточное сообщение
    progress_message = await callback.message.answer("⏳ *Готовлю сводный отчет...*", parse_mode="Markdown")
    await callback.answer()
    
    try:
        # Получаем отчет с учетом выбранного периода
        processor = ReportProcessor(source=Source(source), db_path="accounts.db")
        
        if period == "today":
            report = await processor.get_today_summary_report()
        else:  # period == "yesterday"
            report = await processor.get_yesterday_summary_report()
        
        # Удаляем промежуточное сообщение
        await progress_message.delete()
        
        await callback.message.answer(report, parse_mode="Markdown")
    except Exception as e:
        error_text = str(e).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[").replace("]", "\\]")
        await progress_message.edit_text(f"❌ *Ошибка при подготовке отчета:*\n{error_text}", parse_mode="Markdown")


# --- Получение детальной статистики ---
@router.callback_query(F.data == "get_detailed_report")
async def get_detailed_report(callback: CallbackQuery, state: FSMContext):
    # Получаем список всех аккаунтов для проверки
    accounts = await get_all_accounts(db_path="accounts.db")
    
    if not accounts:
        await callback.message.answer(
            "❌ *Нет доступных аккаунтов*", 
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Сразу предлагаем ввести ID аккаунта
    await callback.message.answer(
        "Введите ID аккаунта для получения детальной статистики:", 
        parse_mode="Markdown"
    )
    await state.set_state(DetailedReportStates.waiting_for_account_id)
    await callback.answer()


@router.message(DetailedReportStates.waiting_for_account_id)
async def process_detailed_report_account_id(message: Message, state: FSMContext):
    try:
        # Пытаемся преобразовать введенный ID в число
        account_id = int(message.text.strip())
        
        # Получаем информацию об аккаунте
        account = await get_account_by_id(account_id, db_path="accounts.db")
        if not account:
            await message.answer(
                "❌ *Аккаунт с указанным ID не найден*\nПопробуйте еще раз или нажмите /menu для возврата в главное меню", 
                parse_mode="Markdown"
            )
            return
        
        # Отправляем промежуточное сообщение
        progress_message = await message.answer(
            f"⏳ *Готовлю детальный отчет для аккаунта {account['account_name']}...*", 
            parse_mode="Markdown"
        )
        
        try:
            # Получаем отчет
            processor = ReportProcessor(source=Source(account['source'].upper()), db_path="accounts.db")
            reports = await processor.get_detailed_report(account_id)
            
            # Удаляем промежуточное сообщение
            await progress_message.delete()
            
            # Отправляем каждый отчет отдельным сообщением
            for report in reports:
                # Если отчет слишком длинный, разбиваем его на части
                if len(report) > 4096:
                    for x in range(0, len(report), 4096):
                        chunk = report[x:x + 4096]
                        await message.answer(chunk, parse_mode="Markdown")
                else:
                    await message.answer(report, parse_mode="Markdown")
            
            # Возвращаем в главное меню
            await message.answer("Выберите действие:", reply_markup=main_menu_keyboard())
            await state.clear()
            
        except Exception as e:
            error_text = str(e).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[").replace("]", "\\]")
            await progress_message.edit_text(f"❌ *Ошибка при подготовке отчета:*\n{error_text}", parse_mode="Markdown")
            await state.clear()
            
    except ValueError:
        await message.answer(
            "❌ *Ошибка: введите корректный числовой ID аккаунта*\nПопробуйте еще раз или нажмите /menu для возврата в главное меню", 
            parse_mode="Markdown"
        )


# --- Обработчик кнопки "Назад" ---
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.answer("Выберите действие:", reply_markup=main_menu_keyboard())
    await callback.answer()


# --- О разработке ---
@router.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    text = (
"""
О боте

Данный бот бесплатный и предзнаначен для мониторинга статистики ваших аккаунтов в Яндекс.Директ.

Реозиторий бота: https://github.com/tonyloks/rnpYandexDirect_tg_bot

Канал разработчика: @poschitai

Поддержать разработку или поблагодарить можно донатом по ссылке: https://yoomoney.ru/to/410011521226963

"""
    )
    await callback.message.answer(text, reply_markup=main_menu_keyboard())
    await callback.answer()


# Добавляем обработчик ошибок
@router.error()
async def error_handler(event: ErrorEvent):
    if isinstance(event.exception, TelegramBadRequest) and "query is too old" in str(event.exception):
        # Если ошибка связана с устаревшим callback query, отправляем сообщение пользователю
        if event.update.callback_query:
            await event.update.callback_query.message.answer(
                "❌ Кнопка устарела. Пожалуйста, используйте актуальное меню:",
                reply_markup=main_menu_keyboard()
            )
