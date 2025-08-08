from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StatesGroup, State
from aiogram.types import FSInputFile

from pathlib import Path

from bot.database.models import Permission
from bot.database.methods import (
    select_today_users, select_admins, get_user_count, select_today_orders,
    select_all_orders, select_today_operations, select_users_balance, select_all_operations,
    select_count_items, select_count_goods, select_count_categories, select_count_bought_items,
    select_bought_item, get_all_admins, get_all_users, check_user, check_user_referrals,
    check_role_name_by_id, select_user_items, select_user_operations
)
from bot.keyboards import back, paginated_keyboard, simple_buttons

from bot.filters import HasPermissionFilter

import datetime

from bot.misc import EnvKeys

router = Router()


class ShopManageFSM(StatesGroup):
    """FSM для сценариев управления магазином."""
    waiting_bought_item_id = State()


# --- Главное меню управления магазином (SHOP_MANAGE)
@router.callback_query(F.data == 'shop_management', HasPermissionFilter(Permission.SHOP_MANAGE))
async def shop_callback_handler(call: CallbackQuery):
    """
    Открывает главное меню управления магазином.
    """
    actions = [
        ("📊 Статистика", "statistics"),
        ("📁 Показать логи", "show_logs"),
        ("👮 Администраторы", "admins_list"),
        ("👤 Пользователи", "users_list"),
        ("🔎 Поиск купленного товара", "show_bought_item"),
        ("⬅️ Назад", "console"),
    ]
    markup = simple_buttons(actions, per_row=1)
    await call.message.edit_text('⛩️ Меню управления магазином', reply_markup=markup)


# --- Показ логов (SHOP_MANAGE)
@router.callback_query(F.data == 'show_logs', HasPermissionFilter(Permission.SHOP_MANAGE))
async def logs_callback_handler(call: CallbackQuery):
    """
    Отправляет файл логов бота, если он существует и не пустой.
    """
    file_path = Path(EnvKeys.BOT_AUDITFILE)
    if file_path.exists() and file_path.stat().st_size > 0:
        doc = FSInputFile(file_path, filename=file_path.name)
        await call.message.bot.send_document(
            chat_id=call.message.chat.id,
            document=doc,
            caption="Логи бота"
        )
    else:
        await call.answer("❗️ Логов пока нет")


# --- Статистика (SHOP_MANAGE)
@router.callback_query(F.data == 'statistics', HasPermissionFilter(Permission.SHOP_MANAGE))
async def statistics_callback_handler(call: CallbackQuery):
    """
    Показывает основные статистики магазина.
    """
    today_str = datetime.date.today().isoformat()

    await call.message.edit_text(
        'Статистика магазина:\n'
        '➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
        '<b>◽ПОЛЬЗОВАТЕЛИ</b>\n'
        f'◾️Пользователей за 24 часа: {select_today_users(today_str)}\n'
        f'◾️Всего администраторов: {select_admins()}\n'
        f'◾️Всего пользователей: {get_user_count()}\n'
        '➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
        '◽<b>СРЕДСТВА</b>\n'
        f'◾Продаж за 24 часа на: {select_today_orders(today_str)}₽\n'
        f'◾Продано товаров на: {select_all_orders()}₽\n'
        f'◾Пополнений за 24 часа: {select_today_operations(today_str)}₽\n'
        f'◾Средств в системе: {select_users_balance()}₽\n'
        f'◾Пополнено: {select_all_operations()}₽\n'
        '➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
        '◽<b>ПРОЧЕЕ</b>\n'
        f'◾Товаров: {select_count_items()} шт.\n'
        f'◾Позиций: {select_count_goods()} шт.\n'
        f'◾Категорий: {select_count_categories()} шт.\n'
        f'◾Продано товаров: {select_count_bought_items()} шт.',
        reply_markup=back("shop_management"),
        parse_mode='HTML'
    )


# --- Список админов (USERS_MANAGE)
@router.callback_query(F.data == 'admins_list', HasPermissionFilter(Permission.USERS_MANAGE))
async def admins_callback_handler(call: CallbackQuery):
    """
    Показывает список админов с пагинацией.
    """
    admins = get_all_admins() or []
    markup = paginated_keyboard(
        items=admins,
        item_text=lambda user_id: str(user_id),
        item_callback=lambda user_id: f"show-user_admin-{user_id}",
        page=0,
        per_page=10,
        back_cb="shop_management",
        nav_cb_prefix="admins-page_",
    )
    await call.message.edit_text('👮 Администраторы бота:', reply_markup=markup)


# --- Навигация по страницам админов
@router.callback_query(F.data.startswith('admins-page_'), HasPermissionFilter(Permission.USERS_MANAGE))
async def navigate_admins(call: CallbackQuery):
    """
    Пагинация по списку админов.
    """
    try:
        current_index = int(call.data.split('_')[1])
    except Exception:
        current_index = 0

    admins = get_all_admins() or []
    markup = paginated_keyboard(
        items=admins,
        item_text=lambda user_id: str(user_id),
        item_callback=lambda user_id: f"show-user_admin-{user_id}",
        page=current_index,
        per_page=10,
        back_cb="shop_management",
        nav_cb_prefix="admins-page_",
    )
    await call.message.edit_text('👮 Администраторы бота:', reply_markup=markup)


# --- Список пользователей (USERS_MANAGE)
@router.callback_query(F.data == 'users_list', HasPermissionFilter(Permission.USERS_MANAGE))
async def users_callback_handler(call: CallbackQuery):
    """
    Показывает список всех пользователей с пагинацией.
    """
    users = [row[0] for row in (get_all_users() or [])]
    markup = paginated_keyboard(
        items=users,
        item_text=lambda user_id: str(user_id),
        item_callback=lambda user_id: f"show-user_user-{user_id}",
        page=0,
        per_page=10,
        back_cb="shop_management",
        nav_cb_prefix="users-page_",
    )
    await call.message.edit_text('Пользователи бота:', reply_markup=markup)


# --- Навигация по страницам пользователей
@router.callback_query(F.data.startswith('users-page_'), HasPermissionFilter(Permission.USERS_MANAGE))
async def navigate_users(call: CallbackQuery):
    """
    Пагинация по списку пользователей.
    """
    try:
        current_index = int(call.data.split('_')[1])
    except Exception:
        current_index = 0

    users = [row[0] for row in (get_all_users() or [])]
    markup = paginated_keyboard(
        items=users,
        item_text=lambda user_id: str(user_id),
        item_callback=lambda user_id: f"show-user_user-{user_id}",
        page=current_index,
        per_page=10,
        back_cb="shop_management",
        nav_cb_prefix="users-page_",
    )
    await call.message.edit_text('Пользователи бота:', reply_markup=markup)


# --- Просмотр информации о пользователе (USERS_MANAGE)
@router.callback_query(F.data.startswith('show-user_'), HasPermissionFilter(permission=Permission.USERS_MANAGE))
async def show_user_info(call: CallbackQuery):
    """
    Показывает подробную инфу о выбранном пользователе.
    """
    query = call.data[10:]
    origin, user_id = query.split('-')  # origin: 'user' | 'admin'
    back_target = "users_list" if origin == "user" else "admins_list"

    user = check_user(user_id)
    user_info = await call.message.bot.get_chat(user_id)
    operations = select_user_operations(user_id)
    overall_balance = sum(operations) if operations else 0
    items = select_user_items(user_id)
    role = check_role_name_by_id(user.role_id)
    referrals = check_user_referrals(user.telegram_id)

    await call.message.edit_text(
        f"👤 <b>Профиль</b> — {user_info.first_name}\n\n"
        f"🆔 <b>ID</b> — <code>{user_id}</code>\n"
        f"💳 <b>Баланс</b> — <code>{user.balance}</code> ₽\n"
        f"💵 <b>Всего пополнено</b> — <code>{overall_balance}</code> ₽\n"
        f"🎁 <b>Куплено товаров</b> — {items} шт\n\n"
        f"👤 <b>Реферал</b> — <code>{user.referral_id}</code>\n"
        f"👥 <b>Рефералы пользователя</b> — {referrals}\n"
        f"🎛 <b>Роль</b> — {role}\n"
        f"🕢 <b>Дата регистрации</b> — <code>{user.registration_date}</code>\n",
        parse_mode='HTML',
        reply_markup=back(back_target)
    )


# --- Поиск купленного товара по уникальному ID (SHOP_MANAGE)
@router.callback_query(F.data == 'show_bought_item', HasPermissionFilter(Permission.SHOP_MANAGE))
async def show_bought_item_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Запрашивает уникальный ID купленного товара для поиска.
    """
    await call.message.edit_text(
        'Введите уникальный ID купленного товара',
        reply_markup=back("shop_management")
    )
    await state.set_state(ShopManageFSM.waiting_bought_item_id)


# --- Обработка ввода уникального ID (SHOP_MANAGE)
@router.message(ShopManageFSM.waiting_bought_item_id, F.text, HasPermissionFilter(Permission.SHOP_MANAGE))
async def process_item_show(message: Message, state: FSMContext):
    """
    Показывает информацию о купленном товаре по его уникальному ID.
    """
    msg = (message.text or "").strip()
    if not msg.isdigit():
        await message.answer(
            '❌ ID должен быть числом.',
            reply_markup=back('show_bought_item')
        )
        return

    item = select_bought_item(int(msg))
    if item:
        await message.answer(
            f'<b>Товар</b>: <code>{item["item_name"]}</code>\n'
            f'<b>Цена</b>: <code>{item["price"]}</code>₽\n'
            f'<b>Дата покупки</b>: <code>{item["bought_datetime"]}</code>\n'
            f'<b>Покупатель</b>: <code>{item["buyer_id"]}</code>\n'
            f'<b>Уникальный ID операции</b>: <code>{item["unique_id"]}</code>\n'
            f'<b>Значение</b>:\n<code>{item["value"]}</code>',
            parse_mode='HTML',
            reply_markup=back('show_bought_item')
        )
    else:
        await message.answer(
            '❌ Товар с указанным уникальным ID не найден',
            reply_markup=back('show_bought_item')
        )

    await state.clear()
