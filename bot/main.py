import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.misc import EnvKeys
from bot.handlers import register_all_handlers
from bot.database.models import register_models
from bot.logger_mesh import configure_logging


async def __on_start_up(dp: Dispatcher) -> None:
    register_all_handlers(dp)
    register_models()


async def start_bot() -> None:
    configure_logging(console=EnvKeys.LOG_TO_STDOUT == "1", debug=EnvKeys.DEBUG == "1")
    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher(storage=MemoryStorage())
    await __on_start_up(dp)

    async with Bot(
            token=EnvKeys.TOKEN,
            default=DefaultBotProperties(
                parse_mode="HTML",
                link_preview_is_disabled=False,
                protect_content=False,
            ),
    ) as bot:
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query", "pre_checkout_query"],
            handle_signals=False,
        )
