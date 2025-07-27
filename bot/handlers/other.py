from aiogram import Dispatcher, Bot
from aiogram.types import CallbackQuery


async def get_bot_user_ids(query):
    bot: Bot = query.bot
    user_id = query.from_user.id
    return bot, user_id


async def check_sub_channel(chat_member):
    return str(chat_member.status) != 'left'


async def get_bot_info(query):
    bot: Bot = query.bot
    bot_info = await bot.me
    username = bot_info.username
    return username


async def close_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    await bot.delete_message(chat_id=call.message.chat.id,
                             message_id=call.message.message_id)


async def dummy_button(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    await bot.answer_callback_query(callback_query_id=call.id, text="")


def register_other_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(close_callback_handler,
                                       lambda c: c.data == 'close')
    dp.register_callback_query_handler(dummy_button,
                                       lambda c: c.data == 'dummy_button')
