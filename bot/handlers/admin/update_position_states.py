from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import ChatNotFound

from bot.database.methods import check_role, check_category, check_item, create_item, add_values_to_item, \
    update_item, delete_item, check_value, delete_only_items
from bot.database.models import Permission
from bot.handlers.other import get_bot_user_ids
from bot.keyboards import goods_management, back, item_management, question_buttons, goods_adding
from bot.logger_mesh import logger
from bot.misc import TgConfig


async def update_item_amount_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'update_amount_of_item'
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("item-management"))
        return
    await call.answer('Недостаточно прав')


async def check_item_name_for_amount_upd(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    item_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    item = check_item(item_name)
    if not item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Товар не может быть добавлен (Такой позиции не существует)',
                                    reply_markup=back('goods_management'))
    else:
        if check_value(item_name) is False:
            TgConfig.STATE[user_id] = 'update_item_values'
            TgConfig.STATE[f'{user_id}_values'] = []
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id,
                text=(
                    'Введите товары для позиции по одному сообщению.\n'
                    'Когда закончите ввод — нажмите «Добавить указанные товары». (появится после первого добавленного товара)'
                ),
                reply_markup=back(r"item-management")
            )
        else:
            await bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=message_id,
                                        text='❌ Товар не может быть добавлен (У данной позиции бесконечный товар)',
                                        reply_markup=back('goods_management'))


async def updating_item_values(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    values = TgConfig.STATE.setdefault(f'{user_id}_values', [])
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    values.append(message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text=f'✅ Товар «{message.text}» добавлен в список ({len(values)} шт.)',
        reply_markup=goods_adding("finish_updating_items", r"item-management")
    )


async def updating_item_amount(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None

    values = TgConfig.STATE.pop(f'{user_id}_values', [])
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item_name = TgConfig.STATE.get(f'{user_id}_name')

    for val in values:
        add_values_to_item(item_name, val, False)

    group_id = TgConfig.GROUP_ID if TgConfig.GROUP_ID != -988765433 else None
    if group_id:
        try:
            await bot.send_message(
                chat_id=group_id,
                text=(
                    f'🎁 Залив\n'
                    f'🏷️ Товар: <b>{item_name}</b>\n'
                    f'📦 Количество: <b>{len(values)}</b>'
                ),
                parse_mode='HTML'
            )
        except ChatNotFound:
            pass

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=message_id,
                                text='✅ Товар добавлен',
                                reply_markup=back(r'item-management'))

    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'добавил товары к позиции "{item_name}" в количестве {len(values)} шт')


async def update_item_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'check_item_name'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("goods_management"))
        return
    await call.answer('Недостаточно прав')


async def check_item_name_for_update(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    item_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    item = check_item(item_name)
    if not item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Позиция не может быть изменена (Такой позиции не существует)',
                                    reply_markup=back('goods_management'))
        return
    TgConfig.STATE[user_id] = 'update_item_name'
    TgConfig.STATE[f'{user_id}_old_name'] = message.text
    TgConfig.STATE[f'{user_id}_category'] = item['category_name']
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите новое имя для позиции:',
                                reply_markup=back('goods_management'))


async def update_item_name(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[f'{user_id}_name'] = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = 'update_item_description'
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите описание для позиции:',
                                reply_markup=back('goods_management'))


async def update_item_description(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[f'{user_id}_description'] = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = 'update_item_price'
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите цену для позиции:',
                                reply_markup=back('goods_management'))


async def update_item_price(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if not message.text.isdigit():
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='⚠️ некорректное значение цены.',
                                    reply_markup=back('goods_management'))
        return
    TgConfig.STATE[f'{user_id}_price'] = message.text
    item_old_name = TgConfig.STATE.get(f'{user_id}_old_name')
    if check_value(item_old_name) is False:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Вы хотите сделать бесконечные товары?',
                                    reply_markup=question_buttons('change_make_infinity', 'goods_management'))
    else:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Вы хотите отменить бесконечные товары?',
                                    reply_markup=question_buttons('change_deny_infinity', 'goods_management'))


async def update_item_process(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    answer = call.data.split('_')
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item_old_name = TgConfig.STATE.get(f'{user_id}_old_name')
    item_new_name = TgConfig.STATE.get(f'{user_id}_name')
    item_description = TgConfig.STATE.get(f'{user_id}_description')
    category = TgConfig.STATE.get(f'{user_id}_category')
    price = TgConfig.STATE.get(f'{user_id}_price')
    if answer[3] == 'no':
        TgConfig.STATE[user_id] = None
        update_item(item_old_name, item_new_name, item_description, price, category)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=message_id,
                                    text='✅ Позиция обновлена',
                                    reply_markup=back('goods_management'))
        admin_info = await bot.get_chat(user_id)
        logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                    f'обновил позицию "{item_old_name}" на "{item_new_name}"')
    else:
        if answer[1] == 'make':
            TgConfig.STATE[user_id] = 'update_item-infinity'

            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=message_id,
                                        text='Введите товар для позиции:',
                                        reply_markup=back('goods_management'))

        elif answer[1] == 'deny':

            TgConfig.STATE[user_id] = 'update_item'
            TgConfig.STATE[f'{user_id}_values'] = []

            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=message_id,
                text=(
                    'Введите товары для позиции по одному сообщению.\n'
                    'Когда закончите ввод — нажмите «Добавить указанные товары». (появится после первого добавленного товара)'
                ),
                reply_markup=back("goods_management")
            )


async def updating_item(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    values = TgConfig.STATE.setdefault(f'{user_id}_values', [])
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    values.append(message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text=f'✅ Товар «{message.text}» добавлен в список ({len(values)} шт.)',
        reply_markup=goods_adding("finish_update_item", "goods_management")
    )


async def update_item_no_infinity(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item_old_name = TgConfig.STATE.get(f'{user_id}_old_name')
    item_new_name = TgConfig.STATE.get(f'{user_id}_name')
    item_description = TgConfig.STATE.get(f'{user_id}_description')
    category = TgConfig.STATE.get(f'{user_id}_category')
    price = TgConfig.STATE.get(f'{user_id}_price')
    values = TgConfig.STATE.pop(f'{user_id}_values', [])
    TgConfig.STATE[user_id] = None

    delete_only_items(item_old_name)

    for val in values:
        add_values_to_item(item_old_name, val, False)

    update_item(item_old_name, item_new_name, item_description, price, category)

    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=message_id,
        text='✅ Позиция обновлена',
        reply_markup=back('goods_management')
    )
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'обновил позицию "{item_old_name}" на "{item_new_name}"')


async def update_item_infinity(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item_old_name = TgConfig.STATE.get(f'{user_id}_old_name')
    item_new_name = TgConfig.STATE.get(f'{user_id}_name')
    item_description = TgConfig.STATE.get(f'{user_id}_description')
    category = TgConfig.STATE.get(f'{user_id}_category')
    price = TgConfig.STATE.get(f'{user_id}_price')
    value = message.text
    TgConfig.STATE[user_id] = None

    delete_only_items(item_old_name)
    add_values_to_item(item_old_name, value, True)
    update_item(item_old_name, item_new_name, item_description, price, category)

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Позиция обновлена',
                                reply_markup=back('goods_management'))

    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'обновил позицию "{item_old_name}" на "{item_new_name}"')


def register_update_management(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(update_item_amount_callback_handler,
                                       lambda c: c.data == 'update_item_amount')
    dp.register_callback_query_handler(updating_item_amount,
                                       lambda c: c.data == 'finish_updating_items')
    dp.register_callback_query_handler(update_item_callback_handler,
                                       lambda c: c.data == 'update_item')
    dp.register_callback_query_handler(update_item_no_infinity,
                                       lambda c: c.data == 'finish_update_item')


    dp.register_message_handler(check_item_name_for_amount_upd,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_amount_of_item')
    dp.register_message_handler(updating_item_values,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_item_values')
    dp.register_message_handler(updating_item,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_item')
    dp.register_message_handler(update_item_infinity,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_item-infinity')
    dp.register_message_handler(check_item_name_for_update,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'check_item_name')
    dp.register_message_handler(update_item_name,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_item_name')
    dp.register_message_handler(update_item_description,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_item_description')
    dp.register_message_handler(update_item_price,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_item_price')

    dp.register_callback_query_handler(update_item_process,
                                       lambda c: c.data.startswith('change_'))