from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StatesGroup, State

from bot.database.models import Permission
from bot.database.methods import (
    check_user, select_user_operations, select_user_items,
    check_role_name_by_id, check_user_referrals, select_bought_items,
    set_role, create_operation, update_balance, get_role_id_by_name
)
from bot.keyboards import back, close, paginated_keyboard, simple_buttons
from bot.logger_mesh import audit_logger
from bot.filters import HasPermissionFilter

import datetime

router = Router()


class UserMgmtStates(StatesGroup):
    """FSM для сценариев управления пользователями."""
    waiting_user_id_for_check = State()
    waiting_user_replenish = State()


# --- Открыть меню управления пользователями
@router.callback_query(F.data == 'user_management', HasPermissionFilter(Permission.USERS_MANAGE))
async def user_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Запрашивает id пользователя для просмотра/изменения данных.
    """
    await state.clear()
    await call.message.edit_text(
        '👤 Введите id пользователя,\nчтобы посмотреть | изменить его данные',
        reply_markup=back('console')
    )
    await state.set_state(UserMgmtStates.waiting_user_id_for_check)


# --- Проверка введённого id пользователя
@router.message(UserMgmtStates.waiting_user_id_for_check, F.text)
async def check_user_data(message: Message, state: FSMContext):
    """
    Проверяет введённый id, если ok — предлагает посмотреть профиль.
    """
    user_id_text = message.text.strip()
    if not user_id_text.isdigit():
        await message.answer(
            '⚠️ Введите корректный числовой ID пользователя.',
            reply_markup=back('console')
        )
        return

    user = check_user(int(user_id_text))
    if not user:
        await message.answer(
            '❌ Профиль недоступен (такого пользователя никогда не существовало)',
            reply_markup=back('console')
        )
        return

    # Кнопки: посмотреть профиль или “назад”
    markup = simple_buttons([
        ("👁 Посмотреть профиль", f"check-user_{user.telegram_id}"),
        ("⬅️ Назад", "user_management")
    ], per_row=1)
    await message.answer(
        f"Вы точно хотите посмотреть профиль пользователя {user.telegram_id}?",
        reply_markup=markup,
        parse_mode='HTML'
    )
    await state.clear()


# --- Просмотр профиля пользователя
@router.callback_query(F.data.startswith('check-user_'), HasPermissionFilter(Permission.USERS_MANAGE))
async def user_profile_view(call: CallbackQuery):
    """
    Показывает админский просмотр профиля пользователя + действия.
    """
    user_id_str = call.data[len('check-user_'):]
    target_id = int(user_id_str)

    user = check_user(target_id)
    if not user:
        await call.answer("❌ Пользователь не найден", show_alert=True)
        return

    user_info = await call.message.bot.get_chat(target_id)

    operations = select_user_operations(target_id)
    overall_balance = sum(operations) if operations else 0
    items = select_user_items(target_id)
    role = check_role_name_by_id(user.role_id)
    referrals = check_user_referrals(user.telegram_id)

    # Кнопки действий
    actions: list[tuple[str, str]] = []
    role_name = role  # 'USER' | 'ADMIN' | 'OWNER'

    if role_name == 'OWNER':  # нельзя трогать владельца
        pass
    elif role_name == 'ADMIN':
        actions.append(("⬇️ Снять администратора", f"remove-admin_{target_id}"))
    else:  # USER
        actions.append(("⬆️ Назначить администратором", f"set-admin_{target_id}"))

    actions.append(("💸 Пополнить баланс", f"fill-user-balance_{target_id}"))
    if items:
        actions.append(("🎁 Купленные товары", f"user-items_{target_id}"))
    actions.append(("⬅️ Назад", "user_management"))

    markup = simple_buttons(actions, per_row=1)
    await call.message.edit_text(
        f"👤 <b>Профиль</b> — {user_info.first_name}\n\n"
        f"🆔 <b>ID</b> — <code>{target_id}</code>\n"
        f"💳 <b>Баланс</b> — <code>{user.balance}</code> ₽\n"
        f"💵 <b>Всего пополнено</b> — <code>{overall_balance}</code> ₽\n"
        f"🎁 <b>Куплено товаров</b> — {items} шт\n\n"
        f"👥 <b>Рефералы пользователя</b> — {referrals}\n"
        f"🎛 <b>Роль</b> — {role}\n"
        f"🕢 <b>Дата регистрации</b> — <code>{user.registration_date}</code>\n",
        parse_mode='HTML',
        reply_markup=markup
    )


# --- Открыть список купленных товаров пользователя (USERS_MANAGE)
@router.callback_query(F.data.startswith('user-items_'), HasPermissionFilter(Permission.USERS_MANAGE))
async def user_items_callback_handler(call: CallbackQuery):
    """
    Показывает купленные товары конкретного пользователя (страница 0).
    Формат callback_data кнопки: user-items_{user_id}
    """
    try:
        user_id = int(call.data[len('user-items_'):])
    except Exception:
        await call.answer("❌ Неверные данные", show_alert=True)
        return

    bought_goods = select_bought_items(user_id) or []

    markup = paginated_keyboard(
        items=bought_goods,
        item_text=lambda item: item.item_name,
        item_callback=lambda item: f"bought-item:{item.id}:bought-goods-page_{user_id}_0",
        page=0,
        per_page=10,
        back_cb=f'check-user_{user_id}',
        nav_cb_prefix=f"bought-goods-page_{user_id}_"
    )
    await call.message.edit_text("Купленные товары:", reply_markup=markup)


# --- Назначение админом
@router.callback_query(F.data.startswith('set-admin_'), HasPermissionFilter(Permission.ADMINS_MANAGE))
async def process_admin_for_purpose(call: CallbackQuery):
    """
    Назначает пользователя админом.
    """
    user_data = call.data[len('set-admin_'):]
    try:
        user_id = int(user_data)
    except Exception:
        await call.answer("❌ Неверные данные", show_alert=True)
        return

    db_user = check_user(user_id)
    if not db_user:
        await call.answer("❌ Пользователь не найден", show_alert=True)
        return

    role_name = check_role_name_by_id(db_user.role_id)
    if role_name == 'OWNER':
        await call.answer("Нельзя менять роль владельца", show_alert=True)
        return

    admin_role_id = get_role_id_by_name('ADMIN')
    set_role(user_id, admin_role_id)

    user_info = await call.message.bot.get_chat(user_id)
    await call.message.edit_text(
        f'✅ Роль присвоена пользователю {user_info.first_name}',
        reply_markup=back(f'check-user_{user_id}')
    )
    try:
        await call.message.bot.send_message(
            chat_id=user_id,
            text='✅ Вам присвоена роль АДМИНИСТРАТОРА бота',
            reply_markup=close()
        )
    except Exception:
        pass

    admin_info = await call.message.bot.get_chat(call.from_user.id)
    audit_logger.info(
        f"Пользователь {call.from_user.id} ({admin_info.first_name}) назначил пользователя {user_id} ({user_info.first_name}) администратором"
    )


# --- Снятие роли админа
@router.callback_query(F.data.startswith('remove-admin_'), HasPermissionFilter(Permission.ADMINS_MANAGE))
async def process_admin_for_remove(call: CallbackQuery):
    """
    Снимает роль админа у пользователя.
    """
    user_data = call.data[len('remove-admin_'):]
    try:
        user_id = int(user_data)
    except Exception:
        await call.answer("❌ Неверные данные", show_alert=True)
        return

    db_user = check_user(user_id)
    if not db_user:
        await call.answer("❌ Пользователь не найден", show_alert=True)
        return

    role_name = check_role_name_by_id(db_user.role_id)
    if role_name == 'OWNER':
        await call.answer("Нельзя снимать роль у владельца", show_alert=True)
        return

    user_role_id = get_role_id_by_name('USER')
    set_role(user_id, user_role_id)

    user_info = await call.message.bot.get_chat(user_id)
    await call.message.edit_text(
        f'✅ Роль отозвана у пользователя {user_info.first_name}',
        reply_markup=back(f'check-user_{user_id}')
    )
    try:
        await call.message.bot.send_message(
            chat_id=user_id,
            text='❌ У вас отозвана роль АДМИНИСТРАТОРА бота',
            reply_markup=close()
        )
    except Exception:
        pass

    admin_info = await call.message.bot.get_chat(call.from_user.id)
    audit_logger.info(
        f"Пользователь {call.from_user.id} ({admin_info.first_name}) отозвал роль администратора у пользователя {user_id} ({user_info.first_name})"
    )


# --- Пополнение баланса пользователя (USERS_MANAGE)
@router.callback_query(F.data.startswith('fill-user-balance_'), HasPermissionFilter(Permission.USERS_MANAGE))
async def replenish_user_balance_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Запрашивает сумму для пополнения баланса выбранного пользователя.
    """
    user_data = call.data[len('fill-user-balance_'):]
    try:
        user_id = int(user_data)
    except Exception:
        await call.answer("❌ Неверные данные", show_alert=True)
        return

    await call.message.edit_text(
        '💰 Введите сумму для пополнения:',
        reply_markup=back(f'check-user_{user_id}')
    )
    await state.set_state(UserMgmtStates.waiting_user_replenish)
    await state.update_data(target_user=user_id)


# --- Обработка суммы пополнения (USERS_MANAGE)
@router.message(UserMgmtStates.waiting_user_replenish, F.text)
async def process_replenish_user_balance(message: Message, state: FSMContext):
    """
    Обрабатывает сумму пополнения баланса пользователя.
    """
    data = await state.get_data()
    user_id = data.get('target_user')

    if not message.text or not message.text.strip().isdigit():
        await message.answer(
            "❌ Неверная сумма пополнения. "
            "Сумма пополнения должна быть числом не меньше 10₽ и не более 10 000₽",
            reply_markup=back(f'check-user_{user_id}')
        )
        return

    amount = int(message.text.strip())
    if not (10 <= amount <= 10000):
        await message.answer(
            "❌ Неверная сумма пополнения. "
            "Сумма пополнения должна быть числом не меньше 10₽ и не более 10 000₽",
            reply_markup=back(f'check-user_{user_id}')
        )
        return

    create_operation(user_id, amount, datetime.datetime.now())
    update_balance(user_id, amount)

    user_info = await message.bot.get_chat(user_id)
    await message.answer(
        f'✅ Баланс пользователя {user_info.first_name} пополнен на {amount}₽',
        reply_markup=back(f'check-user_{user_id}')
    )
    admin_info = await message.bot.get_chat(message.from_user.id)
    audit_logger.info(
        f"Пользователь {message.from_user.id} ({admin_info.first_name}) пополнил баланс пользователя {user_id} ({user_info.first_name}) на {amount}₽"
    )
    try:
        await message.bot.send_message(
            chat_id=user_id,
            text=f'✅ Ваш баланс пополнен на {amount}₽',
            reply_markup=close()
        )
    except Exception:
        pass
    await state.clear()


# --- Проверка профиля (user_manage_check) — просто возвращаемся к профилю пользователя
@router.callback_query(F.data.startswith('check-user_'), HasPermissionFilter(permission=Permission.USERS_MANAGE))
async def check_user_profile_again(call: CallbackQuery):
    """
    Позволяет заново открыть профиль пользователя (переиспользует user_profile_view).
    """
    await user_profile_view(call)
