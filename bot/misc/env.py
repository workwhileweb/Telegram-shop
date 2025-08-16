import os
from abc import ABC
from typing import Final


class EnvKeys(ABC):
    TOKEN: Final = os.environ.get('TOKEN')
    OWNER_ID: Final = os.environ.get('OWNER_ID')
    STARS_PER_VALUE = os.getenv("STARS_PER_VALUE", "0.91")
    TELEGRAM_PROVIDER_TOKEN: Final = os.getenv("TELEGRAM_PROVIDER_TOKEN")
    TELEGRAM_PAY_CURRENCY = os.getenv("TELEGRAM_PAY_CURRENCY", "RUB")
    CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")
    CHANNEL_URL = os.getenv("CHANNEL_URL")
    HELPER_URL = os.getenv("HELPER_URL")
    GROUP_ID = os.getenv("GROUP_ID")
    REFERRAL_PERCENT = os.getenv("REFERRAL_PERCENT", 0)
    PAYMENT_TIME = os.getenv("PAYMENT_TIME", 1800)
    RULES = os.getenv("RULES")
    BOT_LOGFILE = os.getenv("BOT_LOGFILE", "bot.log")
    BOT_AUDITFILE = os.getenv("BOT_AUDITFILE", "audit.log")
