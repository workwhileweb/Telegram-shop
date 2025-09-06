from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.i18n import localize
from bot.database.models import Permission
from bot.database.methods import get_all_users
from bot.keyboards import back, close
from bot.logger_mesh import audit_logger
from bot.filters import HasPermissionFilter
from bot.misc.broadcast_system import BroadcastManager, BroadcastStats
from bot.states import BroadcastFSM

router = Router()

# Global mailing list manager
broadcast_manager: Optional[BroadcastManager] = None


# --- Start broadcast: ask admin for the message text
@router.callback_query(F.data == "send_message", HasPermissionFilter(permission=Permission.BROADCAST))
async def send_message_callback_handler(call: CallbackQuery, state: FSMContext):
    """Beginning of mailing"""
    await call.message.edit_text(
        localize("broadcast.prompt"),
        reply_markup=back("console"),
    )
    await state.set_state(BroadcastFSM.waiting_message)


# --- Receive text and broadcast it to all users
@router.message(BroadcastFSM.waiting_message, F.text)
async def broadcast_messages(message: Message, state: FSMContext):
    """Executing mailing with progress bar"""
    global broadcast_manager

    msg_text = message.text
    users = get_all_users()
    user_ids = [int(row[0]) for row in users]

    await message.delete()

    # Create a progress message
    progress_msg = await message.answer(localize("broadcast.creating",
                                                 ids=len(user_ids)),
                                        reply_markup=back("send_message"))

    # Progress update function
    async def update_progress(stats: BroadcastStats):
        progress = (stats.sent + stats.failed) / stats.total * 100

        try:
            await progress_msg.edit_text(
                localize("broadcast.progress",
                         progress=progress,
                         sent=stats.sent,
                         total=stats.total,
                         failed=stats.failed,
                         time=int((datetime.now() - stats.start_time).total_seconds())),
                reply_markup=back("send_message"))
        except Exception:
            pass  # Ignore update errors

    # Start the mailing
    broadcast_manager = BroadcastManager(
        bot=message.bot,
        batch_size=30,  # 30 messages in parallel
        batch_delay=1.0  # 1 second between batches
    )

    stats = await broadcast_manager.broadcast(
        user_ids=user_ids,
        text=msg_text,
        reply_markup=close(),
        progress_callback=update_progress
    )

    # Final message
    duration = int(stats.duration) if stats.duration else 0
    await progress_msg.edit_text(
        localize("broadcast.done",
                 total=stats.total,
                 sent=stats.sent,
                 failed=stats.failed,
                 blocked=stats.blocked,
                 success=f"{stats.success_rate:.1f}",
                 duration=duration),
        reply_markup=back("send_message"))

    # Logging
    user_info = await message.bot.get_chat(message.from_user.id)
    audit_logger.info(
        f"user {user_info.id} ({user_info.first_name}) sent a broadcast. "
        f"Delivered to {stats.sent}/{stats.total} users in {duration} seconds"
    )

    await state.clear()


@router.callback_query(F.data == "cancel_broadcast", HasPermissionFilter(permission=Permission.BROADCAST))
async def cancel_broadcast_handler(call: CallbackQuery):
    """Cancel current mailing"""
    global broadcast_manager

    if broadcast_manager:
        broadcast_manager.cancel()
        await call.answer(localize("broadcast.cancel"), show_alert=True)
    else:
        await call.answer(localize("broadcast.warning"), show_alert=True)
