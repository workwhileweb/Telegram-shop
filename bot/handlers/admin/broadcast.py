from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StatesGroup, State

from bot.database.models import Permission
from bot.database.methods import get_all_users
from bot.keyboards import back, close
from bot.logger_mesh import audit_logger
from bot.filters import HasPermissionFilter

import asyncio

router = Router()


class BroadcastFSM(StatesGroup):
    waiting_message = State()


# --- Начало рассылки
@router.callback_query(F.data == 'send_message', HasPermissionFilter(permission=Permission.BROADCAST))
async def send_message_callback_handler(call: CallbackQuery, state):
    await call.message.edit_text(
        'Отправьте сообщение для рассылки:',
        reply_markup=back("console")
    )
    await state.set_state(BroadcastFSM.waiting_message)


# --- Получаем текст рассылки, рассылаем всем
@router.message(BroadcastFSM.waiting_message, F.text)
async def broadcast_messages(message: Message, state):
    msg = message.text
    users = get_all_users()
    max_users = 0
    sent = 0

    await message.delete()
    for user_row in users:
        user_id = user_row[0]
        await asyncio.sleep(0.08)
        try:
            await message.bot.send_message(
                chat_id=int(user_id),
                text=msg,
                reply_markup=close()
            )
            sent += 1
        except Exception:
            continue
        max_users += 1

    await message.answer(
        f'Рассылка завершена. Сообщение отправлено {sent} пользователям.',
        reply_markup=back("console")
    )
    user_info = await message.bot.get_chat(message.from_user.id)
    audit_logger.info(
        f"Пользователь {user_info.id} ({user_info.first_name}) совершил рассылку. Рассылка была отправлена {sent} пользователям.")
    await state.clear()
