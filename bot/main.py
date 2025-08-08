import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.misc import EnvKeys
from bot.handlers import register_all_handlers
from bot.database.models import register_models
from bot.logger_mesh import configure_logging

logger, audit = configure_logging(console=False, debug=False)


async def __on_start_up(dp: Dispatcher) -> None:
    register_all_handlers(dp)
    register_models()


async def start_bot():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(
        token=EnvKeys.TOKEN,
        default=DefaultBotProperties(
            parse_mode="HTML",
            link_preview_is_disabled=False,
            protect_content=False  # если нужно — запрет пересылки
        ),
    )
    dp = Dispatcher(storage=MemoryStorage())

    await __on_start_up(dp)
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
