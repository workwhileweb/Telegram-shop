from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.misc import EnvKeys

router = Router()


# Close message
@router.callback_query(F.data == 'close')
async def close_callback_handler(call: CallbackQuery):
    """processing of message closure (deletion)"""
    try:
        await call.message.delete()
    except Exception:
        pass


@router.callback_query(F.data == 'dummy_button')
async def dummy_button(call: CallbackQuery):
    """“Empty” (dummy) button"""
    await call.answer("")


async def check_sub_channel(chat_member) -> bool:
    """channel subscription check"""
    return str(chat_member.status) != 'left'


async def get_bot_info(event) -> str:
    """Bot information (name)"""
    bot = event.bot
    me = await bot.get_me()
    return me.username


def _any_payment_method_enabled() -> bool:
    """Is there at least one enabled payment method?"""
    cryptopay_ok = bool(EnvKeys.CRYPTO_PAY_TOKEN)
    tg_stars_ok = bool(EnvKeys.STARS_PER_VALUE)
    tg_pay_ok = bool(EnvKeys.TELEGRAM_PROVIDER_TOKEN)
    return cryptopay_ok or tg_stars_ok or tg_pay_ok
