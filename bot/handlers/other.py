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
    cryptopay_ok = bool(EnvKeys.CRYPTO_PAY_TOKEN)
    tg_stars_ok = bool(EnvKeys.STARS_PER_VALUE)
    tg_pay_ok = bool(EnvKeys.TELEGRAM_PROVIDER_TOKEN)
    return cryptopay_ok or tg_stars_ok or tg_pay_ok
