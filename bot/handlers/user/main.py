from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums.chat_type import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from urllib.parse import urlparse
import datetime

from bot.database.methods import (
    select_max_role_id, create_user, check_role, check_user,
    select_user_operations, select_user_items, check_user_referrals
)
from bot.handlers.other import check_sub_channel, get_bot_info
from bot.keyboards import main_menu, back, simple_buttons, profile_keyboard
from bot.misc import TgConfig, EnvKeys

# Импортируем дочерние роутеры
from bot.handlers.user.balance_and_payment import router as balance_and_payment_router
from bot.handlers.user.shop_and_goods import router as shop_and_goods_router

router = Router()


# FSM сценарии
class UserStates(StatesGroup):
    main_menu = State()


# --- /start
@router.message(F.text.startswith('/start'))
async def start(message: Message, state: FSMContext):
    """
    Обрабатывает команду /start:
    - Регистрирует пользователя (если новый)
    - Проверяет подписку на канал (если включена)
    - Показывает главное меню
    """
    if message.chat.type != ChatType.PRIVATE:
        return

    user_id = message.from_user.id
    await state.clear()

    owner = select_max_role_id()
    referral_id = message.text[7:] if message.text[7:] != str(user_id) else None
    user_role = owner if str(user_id) == EnvKeys.OWNER_ID else 1
    create_user(telegram_id=user_id, registration_date=datetime.datetime.now(), referral_id=referral_id, role=user_role)

    chat = TgConfig.CHANNEL_URL.lstrip('https://t.me/')
    role_data = check_role(user_id)

    try:
        if chat:
            chat_member = await message.bot.get_chat_member(chat_id=f'@{chat}', user_id=user_id)
            if not await check_sub_channel(chat_member):
                markup = simple_buttons([
                    ("Подписаться", f"https://t.me/{chat}"),
                    ("Проверить", "sub_channel_done")
                ], per_row=1)
                await message.answer('Для начала подпишитесь на новостной канал', reply_markup=markup)
                await message.delete()
                return
    except Exception:
        pass

    markup = main_menu(role=role_data, channel=chat, helper=TgConfig.HELPER_URL)
    await message.answer('⛩️ Основное меню', reply_markup=markup)
    await message.delete()
    await state.set_state(UserStates.main_menu)


# --- Кнопка "назад в меню"
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Возврат пользователя в главное меню.
    """
    user_id = call.from_user.id
    user = check_user(user_id)
    markup = main_menu(role=user.role_id, channel=TgConfig.CHANNEL_URL, helper=TgConfig.HELPER_URL)
    await call.message.edit_text('⛩️ Основное меню', reply_markup=markup)
    await state.set_state(UserStates.main_menu)


# --- Правила
@router.callback_query(F.data == "rules")
async def rules_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Показывает текст правил, если они заданы.
    """
    rules_data = TgConfig.RULES
    if rules_data:
        await call.message.edit_text(rules_data, reply_markup=back("back_to_menu"))
    else:
        await call.answer('❌ Правила не были добавлены')
    await state.clear()


# --- Профиль пользователя
@router.callback_query(F.data == "profile")
async def profile_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Отправляет пользователю его профиль (баланс, покупки, id и т.д.).
    """
    user_id = call.from_user.id
    user = call.from_user
    user_info = check_user(user_id)
    balance = user_info.balance
    operations = select_user_operations(user_id)
    overall_balance = sum(operations) if operations else 0
    items = select_user_items(user_id)
    referral = TgConfig.REFERRAL_PERCENT
    markup = profile_keyboard(referral, items)
    await call.message.edit_text(
        f"👤 <b>Профиль</b> — {user.first_name}\n"
        f"🆔 <b>ID</b> — <code>{user_id}</code>\n"
        f"💳 <b>Баланс</b> — <code>{balance}</code> ₽\n"
        f"💵 <b>Всего пополнено</b> — <code>{overall_balance}</code> ₽\n"
        f"🎁 <b>Куплено товаров</b> — {items} шт",
        reply_markup=markup,
        parse_mode='HTML'
    )
    await state.clear()


# --- Реферальная система
@router.callback_query(F.data == "referral_system")
async def referral_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Показывает информацию о рефералах и реферальную ссылку пользователя.
    """
    user_id = call.from_user.id
    referrals = check_user_referrals(user_id)
    referral_percent = TgConfig.REFERRAL_PERCENT
    bot_username = await get_bot_info(call)
    await call.message.edit_text(
        f'💚 Реферальная система\n'
        f'🔗 Ссылка: https://t.me/{bot_username}?start={user_id}\n'
        f'Количество рефералов: {referrals}\n'
        f'📔 Реферальная система позволит Вам заработать деньги без всяких вложений. '
        f'Необходимо всего лишь распространять свою реферальную ссылку и Вы будете получать '
        f'{referral_percent}% от суммы пополнений Ваших рефералов на Ваш баланс бота.',
        reply_markup=back('profile')
    )
    await state.clear()


# --- Проверка подписки (после клика "Проверить")
@router.callback_query(F.data == "sub_channel_done")
async def check_sub_to_channel(call: CallbackQuery, state: FSMContext):
    """
    Проверяет подписку пользователя на канал после нажатия "Проверить".
    """
    user_id = call.from_user.id
    chat = TgConfig.CHANNEL_URL
    parsed_url = urlparse(chat)
    channel_username = parsed_url.path.lstrip('/')
    helper = TgConfig.HELPER_URL
    chat_member = await call.bot.get_chat_member(chat_id='@' + channel_username, user_id=user_id)

    if await check_sub_channel(chat_member):
        user = check_user(user_id)
        role = user.role_id
        markup = main_menu(role, chat, helper)
        await call.message.edit_text('⛩️ Основное меню', reply_markup=markup)
        await state.set_state(UserStates.main_menu)
    else:
        await call.answer('Вы не подписались')


# Подключаем все вложенные роутеры (user-разделы)
router.include_router(balance_and_payment_router)
router.include_router(shop_and_goods_router)
