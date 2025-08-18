from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StatesGroup, State

from bot.i18n import localize
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

from bot.misc import EnvKeys

router = Router()


class UserMgmtStates(StatesGroup):
    """FSM for user management flow."""
    waiting_user_id_for_check = State()
    waiting_user_replenish = State()


# --- Open user management menu
@router.callback_query(F.data == 'user_management', HasPermissionFilter(Permission.USERS_MANAGE))
async def user_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Asks admin to enter a user's ID to view / modify.
    """
    await state.clear()
    await call.message.edit_text(
        localize('admin.users.prompt_enter_id'),
        reply_markup=back('console')
    )
    await state.set_state(UserMgmtStates.waiting_user_id_for_check)


# --- Validate entered user id
@router.message(UserMgmtStates.waiting_user_id_for_check, F.text)
async def check_user_data(message: Message, state: FSMContext):
    """
    Validates ID and shows a confirmation to open profile.
    """
    user_id_text = message.text.strip()
    if not user_id_text.isdigit():
        await message.answer(
            localize('admin.users.invalid_id'),
            reply_markup=back('console')
        )
        return

    user = check_user(int(user_id_text))
    if not user:
        await message.answer(
            localize('admin.users.profile_unavailable'),
            reply_markup=back('console')
        )
        return

    # Buttons: view profile or go back
    markup = simple_buttons([
        (localize('btn.admin.view_profile'), f"check-user_{user.telegram_id}"),
        (localize('btn.back'), "user_management")
    ], per_row=1)
    await message.answer(
        localize('admin.users.confirm_view', id=user.telegram_id),
        reply_markup=markup,
        parse_mode='HTML'
    )
    await state.clear()


# --- View user profile
@router.callback_query(F.data.startswith('check-user_'), HasPermissionFilter(Permission.USERS_MANAGE))
async def user_profile_view(call: CallbackQuery):
    """
    Shows admin view of user profile + actions.
    """
    user_id_str = call.data[len('check-user_'):]
    try:
        target_id = int(user_id_str)
    except Exception:
        await call.answer(localize('errors.invalid_data'), show_alert=True)
        return

    user = check_user(target_id)
    if not user:
        await call.answer(localize('admin.users.not_found'), show_alert=True)
        return

    user_info = await call.message.bot.get_chat(target_id)

    operations = select_user_operations(target_id)
    overall_balance = sum(operations) if operations else 0
    items_count = select_user_items(target_id)
    role = check_role_name_by_id(user.role_id)
    referrals = check_user_referrals(user.telegram_id)

    # Action buttons
    actions: list[tuple[str, str]] = []
    role_name = role  # 'USER' | 'ADMIN' | 'OWNER'

    if role_name == 'OWNER':
        # Do nothing: owner’s role is immutable for safety
        pass
    elif role_name == 'ADMIN':
        actions.append((localize('btn.admin.demote'), f"remove-admin_{target_id}"))
    else:  # USER
        actions.append((localize('btn.admin.promote'), f"set-admin_{target_id}"))

    actions.append((localize('btn.admin.replenish_user'), f"fill-user-balance_{target_id}"))
    if items_count:
        actions.append((localize('btn.purchased'), f"user-items_{target_id}"))
    actions.append((localize('btn.back'), "user_management"))

    markup = simple_buttons(actions, per_row=1)

    lines = [
        localize('profile.caption', name=user_info.first_name),
        '',
        localize('profile.id', id=target_id),
        localize('profile.balance', amount=user.balance, currency=EnvKeys.PAY_CURRENCY),
        localize('profile.total_topup', amount=overall_balance, currency=EnvKeys.PAY_CURRENCY),
        localize('profile.purchased_count', count=items_count),
        '',
        localize('admin.users.referrals', count=referrals),
        localize('admin.users.role', role=role),
        localize('profile.registration_date', dt=user.registration_date),
    ]
    await call.message.edit_text(
        '\n'.join(lines),
        parse_mode='HTML',
        reply_markup=markup
    )


# --- Open bought items of the user (USERS_MANAGE)
@router.callback_query(F.data.startswith('user-items_'), HasPermissionFilter(Permission.USERS_MANAGE))
async def user_items_callback_handler(call: CallbackQuery):
    """
    Shows bought items of a specific user (page 0).
    Callback data format: user-items_{user_id}
    """
    try:
        user_id = int(call.data[len('user-items_'):])
    except Exception:
        await call.answer(localize('errors.invalid_data'), show_alert=True)
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
    await call.message.edit_text(localize('purchases.title'), reply_markup=markup)


# --- Promote to admin
@router.callback_query(F.data.startswith('set-admin_'), HasPermissionFilter(Permission.ADMINS_MANAGE))
async def process_admin_for_purpose(call: CallbackQuery):
    """
    Assigns ADMIN role to the user.
    """
    user_data = call.data[len('set-admin_'):]
    try:
        user_id = int(user_data)
    except Exception:
        await call.answer(localize('errors.invalid_data'), show_alert=True)
        return

    db_user = check_user(user_id)
    if not db_user:
        await call.answer(localize('admin.users.not_found'), show_alert=True)
        return

    role_name = check_role_name_by_id(db_user.role_id)
    if role_name == 'OWNER':
        await call.answer(localize('admin.users.cannot_change_owner'), show_alert=True)
        return

    admin_role_id = get_role_id_by_name('ADMIN')
    set_role(user_id, admin_role_id)

    user_info = await call.message.bot.get_chat(user_id)
    await call.message.edit_text(
        localize('admin.users.set_admin.success', name=user_info.first_name),
        reply_markup=back(f'check-user_{user_id}')
    )
    try:
        await call.message.bot.send_message(
            chat_id=user_id,
            text=localize('admin.users.set_admin.notify'),
            reply_markup=close()
        )
    except Exception:
        pass

    admin_info = await call.message.bot.get_chat(call.from_user.id)
    audit_logger.info(
        f"User {call.from_user.id} ({admin_info.first_name}) assigned user"
        f"{user_id} ({user_info.first_name}) as administrator"
    )


# --- Demote from admin
@router.callback_query(F.data.startswith('remove-admin_'), HasPermissionFilter(Permission.ADMINS_MANAGE))
async def process_admin_for_remove(call: CallbackQuery):
    """
    Revokes ADMIN role from the user (sets USER).
    """
    user_data = call.data[len('remove-admin_'):]
    try:
        user_id = int(user_data)
    except Exception:
        await call.answer(localize('errors.invalid_data'), show_alert=True)
        return

    db_user = check_user(user_id)
    if not db_user:
        await call.answer(localize('admin.users.not_found'), show_alert=True)
        return

    role_name = check_role_name_by_id(db_user.role_id)
    if role_name == 'OWNER':
        await call.answer(localize('admin.users.cannot_change_owner'), show_alert=True)
        return

    user_role_id = get_role_id_by_name('USER')
    set_role(user_id, user_role_id)

    user_info = await call.message.bot.get_chat(user_id)
    await call.message.edit_text(
        localize('admin.users.remove_admin.success', name=user_info.first_name),
        reply_markup=back(f'check-user_{user_id}')
    )
    try:
        await call.message.bot.send_message(
            chat_id=user_id,
            text=localize('admin.users.remove_admin.notify'),
            reply_markup=close()
        )
    except Exception:
        pass

    admin_info = await call.message.bot.get_chat(call.from_user.id)
    audit_logger.info(
        f"User {call.from_user.id} ({admin_info.first_name}) revoked the role administrator"
        f" from the user {user_id} ({user_info.first_name})"
    )


# --- Ask amount for admin top-up (USERS_MANAGE)
@router.callback_query(F.data.startswith('fill-user-balance_'), HasPermissionFilter(Permission.USERS_MANAGE))
async def replenish_user_balance_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Asks for amount to top up selected user's balance.
    """
    user_data = call.data[len('fill-user-balance_'):]
    try:
        user_id = int(user_data)
    except Exception:
        await call.answer(localize('errors.invalid_data'), show_alert=True)
        return

    await call.message.edit_text(
        localize('payments.replenish_prompt', currency=EnvKeys.PAY_CURRENCY),
        reply_markup=back(f'check-user_{user_id}')
    )
    await state.set_state(UserMgmtStates.waiting_user_replenish)
    await state.update_data(target_user=user_id)


# --- Process admin top-up amount (USERS_MANAGE)
@router.message(UserMgmtStates.waiting_user_replenish, F.text)
async def process_replenish_user_balance(message: Message, state: FSMContext):
    """
    Processes entered amount and tops up user's balance.
    """
    data = await state.get_data()
    user_id = data.get('target_user')

    # Validation
    min_amount, max_amount = EnvKeys.MIN_AMOUNT, EnvKeys.MAX_AMOUNT
    text = (message.text or '').strip()
    if not text.isdigit():
        await message.answer(
            localize('payments.replenish_invalid', min_amount=min_amount, max_amount=max_amount),
            reply_markup=back(f'check-user_{user_id}')
        )
        return

    amount = int(text)
    if not (min_amount <= amount <= max_amount):
        await message.answer(
            localize('payments.replenish_invalid', min_amount=min_amount, max_amount=max_amount),
            reply_markup=back(f'check-user_{user_id}')
        )
        return

    # Apply top-up
    create_operation(user_id, amount, datetime.datetime.now())
    update_balance(user_id, amount)

    user_info = await message.bot.get_chat(user_id)
    await message.answer(
        localize('admin.users.balance.topped', name=user_info.first_name, amount=amount, currency=EnvKeys.PAY_CURRENCY),
        reply_markup=back(f'check-user_{user_id}')
    )

    admin_info = await message.bot.get_chat(message.from_user.id)
    audit_logger.info(
        f"User {message.from_user.id} ({admin_info.first_name}) topped up the balance of user "
        f"{user_id} ({user_info.first_name}) by {amount}"
    )
    try:
        await message.bot.send_message(
            chat_id=user_id,
            text=localize('admin.users.balance.topped.notify', amount=amount, currency=EnvKeys.PAY_CURRENCY),
            reply_markup=close()
        )
    except Exception:
        pass
    await state.clear()


# --- Re-open profile from various places
@router.callback_query(F.data.startswith('check-user_'), HasPermissionFilter(permission=Permission.USERS_MANAGE))
async def check_user_profile_again(call: CallbackQuery):
    """
    Re-uses user_profile_view to show the profile again.
    """
    await user_profile_view(call)
