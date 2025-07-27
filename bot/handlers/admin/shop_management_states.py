import datetime
import os

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from bot.database.methods import check_role, select_today_users, select_admins, get_user_count, select_today_orders, \
    select_all_orders, select_today_operations, select_users_balance, select_all_operations, select_count_items, \
    select_count_goods, select_count_categories, select_count_bought_items, select_bought_item, get_all_admins, \
    get_all_users, check_user, check_user_referrals, check_role_name_by_id, select_user_items, select_user_operations
from bot.database.models import Permission
from bot.handlers.other import get_bot_user_ids
from bot.keyboards import shop_management, back, users_list, statistic_buttons
from bot.misc import TgConfig


async def shop_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('⛩️ Меню управления магазином',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=shop_management())
        return
    await call.answer('Недостаточно прав')


async def logs_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    file_path = 'bot.log'
    if role >= Permission.SHOP_MANAGE:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'rb') as document:
                await bot.send_document(chat_id=call.message.chat.id,
                                        document=document)
                return
        else:
            await call.answer(text="❗️ Логов пока нет")
            return
    await call.answer('Недостаточно прав')


async def statistics_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        await bot.edit_message_text('Статистика магазина:\n'
                                    '➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                    '<b>◽ПОЛЬЗОВАТЕЛИ</b>\n'
                                    f'◾️Пользователей за 24 часа: {select_today_users(today)}\n'
                                    f'◾️Всего администраторов: {select_admins()}\n'
                                    f'◾️Всего пользователей: {get_user_count()}\n'
                                    '➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                    '◽<b>СРЕДСТВА</b>\n'
                                    f'◾Продаж за 24 часа на: {select_today_orders(today)}₽\n'
                                    f'◾Продано товаров на: {select_all_orders()}₽\n'
                                    f'◾Пополнений за 24 часа: {select_today_operations(today)}₽\n'
                                    f'◾Средств в системе: {select_users_balance()}₽\n'
                                    f'◾Пополнено: {select_all_operations()}₽\n'
                                    '➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                    '◽<b>ПРОЧЕЕ</b>\n'
                                    f'◾Товаров: {select_count_items()}шт.\n'
                                    f'◾Позиций: {select_count_goods()}шт.\n'
                                    f'◾Категорий: {select_count_categories()}шт.\n'
                                    f'◾Продано товаров: {select_count_bought_items()}шт.',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=statistic_buttons(),
                                    parse_mode='HTML')
        return
    await call.answer('Недостаточно прав')


async def admins_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.USERS_MANAGE:
        admins = get_all_admins()
        max_index = len(admins) // 10
        if len(admins) % 10 == 0:
            max_index -= 1
        markup = users_list(admins, 0, max_index, "admins")
        await bot.edit_message_text('👮 Администраторы бота:',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=markup)
        return
    await call.answer('Недостаточно прав')


async def navigate_admins(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    admins = get_all_admins()
    current_index = int(call.data.split('_')[1])
    max_index = len(admins) // 10
    if len(admins) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        markup = users_list(admins, current_index, max_index, "admins")
        await bot.edit_message_text('👮 Администраторы бота:',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=markup)
    else:
        await call.answer('❌ Такой страницы нет')


async def users_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.USERS_MANAGE:
        users = [x[0] for x in get_all_users()]
        max_index = len(users) // 10
        if len(users) % 10 == 0:
            max_index -= 1
        markup = users_list(users, 0, max_index)
        await bot.edit_message_text('Пользователи бота:',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=markup)
        return
    await call.answer('Недостаточно прав')


async def navigate_users(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    users = [x[0] for x in get_all_users()]
    current_index = int(call.data.split('_')[1])
    max_index = len(users) // 10
    if len(users) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        markup = users_list(users, current_index, max_index)
        await bot.edit_message_text('Пользователи бота:',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=markup)
    else:
        await call.answer('❌ Такой страницы нет')


async def show_user_info(call: CallbackQuery):
    query = call.data[10:]
    back_data = query.split('-')[0]
    user_id = query.split('-')[1]
    bot, admin_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    TgConfig.STATE[f'{admin_id}_user_data'] = user_id
    user = check_user(user_id)
    user_info = await bot.get_chat(user_id)
    operations = select_user_operations(user_id)
    overall_balance = 0
    if operations:
        for i in operations:
            overall_balance += i
    items = select_user_items(user_id)
    role = check_role_name_by_id(user.role_id)
    referrals = check_user_referrals(user.telegram_id)
    text = """
ПОДРОБНАЯ ИНФОРМАЦИЯ И ВОЗМОЖНОСТЬ ВЗАИМОДЕЙТСВИЯ ДОСТУПНА В РАЗДЕЛЕ
          "Управление пользователями"
    """
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=f'<b>{text}</b>\n\n'
                                     f"👤 <b>Профиль</b> — {user_info.first_name}\n\n🆔"
                                     f" <b>ID</b> — <code>{user_id}</code>\n"
                                     f"💳 <b>Баланс</b> — <code>{user.balance}</code> ₽\n"
                                     f"💵 <b>Всего пополнено</b> — <code>{overall_balance}</code> ₽\n"
                                     f"🎁 <b>Куплено товаров</b> — {items} шт\n\n"
                                     f"👤 <b>Реферал</b> — <code>{user.referral_id}</code>\n"
                                     f"👥 <b>Рефералы пользователя</b> — {referrals}\n"
                                     f"🎛 <b>Роль</b> — {role}\n"
                                     f"🕢 <b>Дата регистрации</b> — <code>{user.registration_date}</code>\n",
                                parse_mode='HTML',
                                reply_markup=back(back_data))


async def show_bought_item_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'show_item'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите уникальный ID купленного товара',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("goods_management"))
        return
    await call.answer('Недостаточно прав')


async def process_item_show(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    item = select_bought_item(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text=f'<b>Товар</b>: <code>{item["item_name"]}</code>\n'
                                         f'<b>Цена</b>: <code>{item["price"]}</code>₽\n'
                                         f'<b>Дата покупки</b>: <code>{item["bought_datetime"]}</code>\n'
                                         f'<b>Покупатель</b>: <code>{item["buyer_id"]}</code>\n'
                                         f'<b>Уникальный ID операции</b>: <code>{item["unique_id"]}</code>\n'
                                         f'<b>Значение</b>:\n<code>{item["value"]}</code>',
                                    parse_mode='HTML',
                                    reply_markup=back('show_bought_item'))
        return
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='❌ Товар с указанным уникальным ID не найден',
                                reply_markup=back('show_bought_item'))


def register_shop_management(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(statistics_callback_handler,
                                       lambda c: c.data == 'statistics')
    dp.register_callback_query_handler(show_bought_item_callback_handler,
                                       lambda c: c.data == 'show_bought_item')
    dp.register_callback_query_handler(shop_callback_handler,
                                       lambda c: c.data == 'shop_management')
    dp.register_callback_query_handler(logs_callback_handler,
                                       lambda c: c.data == 'show_logs')
    dp.register_callback_query_handler(admins_callback_handler,
                                       lambda c: c.data == 'admins_list')
    dp.register_callback_query_handler(users_callback_handler,
                                       lambda c: c.data == 'users_list')

    dp.register_callback_query_handler(navigate_admins,
                                       lambda c: c.data.startswith('admins-page_'))
    dp.register_callback_query_handler(navigate_users,
                                       lambda c: c.data.startswith('users-page_'))
    dp.register_callback_query_handler(show_user_info,
                                       lambda c: c.data.startswith('show-user_'))

    dp.register_message_handler(process_item_show,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'show_item')
