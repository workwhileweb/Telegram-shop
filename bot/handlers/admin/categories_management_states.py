from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from bot.database.methods import check_role, check_category, create_category, delete_category, update_category
from bot.database.models import Permission
from bot.handlers.other import get_bot_user_ids
from bot.keyboards import categories_management, back
from bot.logger_mesh import logger
from bot.misc import TgConfig


async def categories_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('⛩️ Меню управления категориями',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=categories_management())
        return
    await call.answer('Недостаточно прав')


async def add_category_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'add_category'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название категории',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("categories_management"))
        return
    await call.answer('Недостаточно прав')


async def process_category_for_add(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    category = check_category(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if category:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Категория не создана (Такая категория уже существует)',
                                    reply_markup=back('categories_management'))
        return
    create_category(msg)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Категория создана',
                                reply_markup=back('categories_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'создал новую категорию "{msg}"')


async def delete_category_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'delete_category'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название категории',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("categories_management"))
        return
    await call.answer('Недостаточно прав')


async def process_category_for_delete(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    category = check_category(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if not category:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Категория не удалена (Такой категории не существует)',
                                    reply_markup=back('categories_management'))
        return
    delete_category(msg)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Категория удалена',
                                reply_markup=back('categories_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'удалил категорию "{category["name"]}"')


async def update_category_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'check_category'
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название категории для обновления:',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("categories_management"))
        return
    await call.answer('Недостаточно прав')


async def check_category_for_update(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    category_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    category = check_category(category_name)
    if not category:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Категория не может быть обновлена (Такой категории не существует)',
                                    reply_markup=back('categories_management'))
        return
    TgConfig.STATE[user_id] = 'update_category_name'
    TgConfig.STATE[f'{user_id}_check_category'] = message.text
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите новое имя для категории:',
                                reply_markup=back('categories_management'))


async def check_category_name_for_update(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    category = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    old_name = TgConfig.STATE.get(f'{user_id}_check_category')
    TgConfig.STATE[user_id] = None
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    update_category(old_name, category)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text=f'✅ Категория "{category}" обновлена успешно.',
                                reply_markup=back('categories_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'изменил категорию "{old_name}" на "{category}"')


def register_categories_management(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(categories_callback_handler,
                                       lambda c: c.data == 'categories_management')
    dp.register_callback_query_handler(add_category_callback_handler,
                                       lambda c: c.data == 'add_category')
    dp.register_callback_query_handler(delete_category_callback_handler,
                                       lambda c: c.data == 'delete_category')
    dp.register_callback_query_handler(update_category_callback_handler,
                                       lambda c: c.data == 'update_category')

    dp.register_message_handler(process_category_for_add,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'add_category')
    dp.register_message_handler(process_category_for_delete,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'delete_category')
    dp.register_message_handler(check_category_for_update,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'check_category')
    dp.register_message_handler(check_category_name_for_update,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_category_name')