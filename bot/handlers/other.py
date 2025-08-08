from decimal import Decimal, ROUND_HALF_UP

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.misc import EnvKeys

router = Router()


# --- Закрыть сообщение
@router.callback_query(F.data == 'close')
async def close_callback_handler(call: CallbackQuery):
    try:
        await call.message.delete()
    except Exception:
        pass


# --- “Пустая” кнопка
@router.callback_query(F.data == 'dummy_button')
async def dummy_button(call: CallbackQuery):
    await call.answer("")


async def check_sub_channel(chat_member) -> bool:
    return str(chat_member.status) != 'left'


async def get_bot_info(event) -> str:
    bot = event.bot
    me = await bot.get_me()
    return me.username


def _any_payment_method_enabled() -> bool:
    """Есть ли хотя бы один включённый метод оплаты."""
    yoomoney_ok = bool(EnvKeys.ACCESS_TOKEN and EnvKeys.ACCOUNT_NUMBER)
    cryptopay_ok = bool(EnvKeys.CRYPTO_PAY_TOKEN)
    return yoomoney_ok or cryptopay_ok
