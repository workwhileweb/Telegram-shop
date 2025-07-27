from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from bot.keyboards import console
from bot.database.methods import check_role
from bot.misc import TgConfig

from bot.handlers.admin.broadcast import register_mailing
from bot.handlers.admin.shop_management_states import register_shop_management
from bot.handlers.admin.user_management_states import register_user_management
from bot.handlers.admin.categories_management_states import register_categories_management
from bot.handlers.admin.goods_management_states import register_goods_management
from bot.handlers.admin.adding_position_states import register_add_management
from bot.handlers.admin.update_position_states import register_update_management
from bot.handlers.other import get_bot_user_ids


async def console_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role > 1:
        await bot.edit_message_text('⛩️ Меню администратора',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=console())


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(console_callback_handler,
                                       lambda c: c.data == 'console')

    register_mailing(dp)
    register_shop_management(dp)
    register_user_management(dp)
    register_categories_management(dp)
    register_goods_management(dp)
    register_add_management(dp)
    register_update_management(dp)
