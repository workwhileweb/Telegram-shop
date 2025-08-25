from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.i18n import localize
from bot.database.models import Permission
from bot.database.methods import get_all_users
from bot.keyboards import back, close
from bot.logger_mesh import audit_logger
from bot.filters import HasPermissionFilter
from bot.states import BroadcastFSM

import asyncio

router = Router()


# --- Start broadcast: ask admin for the message text
@router.callback_query(F.data == "send_message", HasPermissionFilter(permission=Permission.BROADCAST))
async def send_message_callback_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        localize("broadcast.prompt"),
        reply_markup=back("console"),
    )
    await state.set_state(BroadcastFSM.waiting_message)


# --- Receive text and broadcast it to all users
@router.message(BroadcastFSM.waiting_message, F.text)
async def broadcast_messages(message: Message, state: FSMContext):
    msg = message.text
    users = get_all_users()

    await message.delete()

    sent = 0
    for row in users:
        user_id = int(row[0])
        # small delay to respect rate limits
        await asyncio.sleep(0.08)
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=msg,
                reply_markup=close(),
            )
            sent += 1
        except Exception:
            # ignore delivery errors (blocked bot, etc.)
            continue

    await message.answer(
        localize("broadcast.done", count=sent),
        reply_markup=back("console"),
    )

    user_info = await message.bot.get_chat(message.from_user.id)
    audit_logger.info(
        f"user {user_info.id} ({user_info.first_name}) sent a broadcast."
        f"The Broadcast has been sent to {sent} users."
    )
    await state.clear()
