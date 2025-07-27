from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from bot.database.methods import check_role, check_item, delete_item, select_items, get_item_info, \
    get_goods_info, delete_item_from_position
from bot.database.models import Permission
from bot.handlers.other import get_bot_user_ids
from bot.keyboards import goods_management, back, item_management, goods_in_item_list, delete_question
from bot.logger_mesh import logger
from bot.misc import TgConfig


async def goods_management_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('⛩️ Меню управления позициями',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=goods_management())
        return
    await call.answer('Недостаточно прав')


async def goods_settings_menu_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('⛩️ Выберите действие для позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=item_management())
        return
    await call.answer('Недостаточно прав')


async def delete_item_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'process_removing_item'
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("goods_management"))
        return
    await call.answer('Недостаточно прав')


async def delete_str_item(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item = check_item(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if not item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Позиция не удалена (Такой позиции не существует)',
                                    reply_markup=back('goods_management'))
        return
    delete_item(msg)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Позиция удалена',
                                reply_markup=back('goods_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'удалил позицию "{msg}"')


async def show_items_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'process_show_item'
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("goods_management"))
        return
    await call.answer('Недостаточно прав')


async def show_str_item(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item = check_item(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if not item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Товаров нет (Такой позиции не существует)',
                                    reply_markup=back('goods_management'))
        return
    goods = select_items(msg)
    max_index = len(goods) // 10
    if len(goods) % 10 == 0:
        max_index -= 1
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Товары в позиции',
                                reply_markup=goods_in_item_list(goods, msg, 0, max_index))


async def navigate_items_in_goods(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    item_name = call.data.split('_')[1]
    current_index = int(call.data.split('_')[2])
    goods = select_items(item_name)
    max_index = len(goods) // 10
    if len(goods) % 10 == 0:
        max_index -= 1
    if 0 <= current_index <= max_index:
        markup = goods_in_item_list(goods, item_name, 0, max_index)
        await bot.edit_message_text(message_id=call.message.message_id,
                                    chat_id=call.message.chat.id,
                                    text='🏪 выберите нужный товар',
                                    reply_markup=markup)
    else:
        await bot.answer_callback_query(callback_query_id=call.id, text="❌ Такой страницы нет")


async def item_info_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None

    item = call.data.split("_")[1]
    back_data = "_".join(call.data.split("_")[3:])

    item_info = get_goods_info(item)
    position_info = get_item_info(item_info["item_name"])
    markup = delete_question(item, back_data) if check_role(user_id) >= Permission.SHOP_MANAGE else back(back_data)
    await bot.edit_message_text(
        f'<b>Позиция</b>: <code>{item_info["item_name"]}</code>\n'
        f'<b>Цена</b>: <code>{position_info["price"]}</code>₽\n'
        f'<b>Уникальный ID</b>: <code>{item_info["id"]}</code>\n'
        f'<b>Товар</b>:\n<code>{item_info["value"]}</code>',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup)


async def process_delete_item_from_position(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None

    item = call.data.split("_")[1]
    back_data = "_".join(call.data.split("_")[2:])

    item_info = get_goods_info(item)
    position = item_info["item_name"]
    delete_item_from_position(item)

    await bot.edit_message_text(
        f'✅ Товар удалён',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=back(back_data))

    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'удалил товар с id={item} из позиции {position}')


def register_goods_management(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(goods_settings_menu_callback_handler,
                                       lambda c: c.data == 'item-management')
    dp.register_callback_query_handler(delete_item_callback_handler,
                                       lambda c: c.data == 'delete_item')
    dp.register_callback_query_handler(goods_management_callback_handler,
                                       lambda c: c.data == 'goods_management')
    dp.register_callback_query_handler(show_items_callback_handler,
                                       lambda c: c.data == 'show__items_in_position')

    dp.register_message_handler(delete_str_item,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'process_removing_item')
    dp.register_message_handler(show_str_item,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'process_show_item')

    dp.register_callback_query_handler(navigate_items_in_goods,
                                       lambda c: c.data.startswith('goods-in-item-page_'))
    dp.register_callback_query_handler(item_info_callback_handler,
                                       lambda c: c.data.startswith('show-item_'))
    dp.register_callback_query_handler(process_delete_item_from_position,
                                       lambda c: c.data.startswith('delete-item-from-position_'))
