import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from bot.misc import EnvKeys

LOG_PATH = EnvKeys.BOT_LOGFILE
AUDIT_PATH = EnvKeys.BOT_AUDITFILE


def configure_logging(console: bool = False, debug: bool = False) -> tuple[logging.Logger, logging.Logger]:
    """
    Configures project logging:
    - application logger "telegram_shop" -> file (UTF-8, rotation)
    - separate audit-logger "telegram_shop.audit" -> file (UTF-8, by days)
    """
    # 0) root - without handlers and on WARNING
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(logging.WARNING)

    # 1) main logger
    logger = logging.getLogger("telegram_shop")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = RotatingFileHandler(
        LOG_PATH, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    file_handler.setFormatter(fmt)
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        logger.addHandler(file_handler)

    # 2) audit-logger — only important actions (product creation, role change, etc.)
    audit_logger = logging.getLogger("telegram_shop.audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False

    audit_handler = TimedRotatingFileHandler(
        AUDIT_PATH, when="midnight", backupCount=14, encoding="utf-8", utc=False
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(logging.Formatter("%(asctime)s\t%(message)s"))
    if not any(isinstance(h, TimedRotatingFileHandler) for h in audit_logger.handlers):
        audit_logger.addHandler(audit_handler)

    # 3) Mute external loggers.
    for name in [
        "aiogram", "aiogram.event", "aiogram.dispatcher", "aiogram.client", "aiohttp", "aiogram.client.telegram",
        "aiogram.client.session.aiohttp", "aiohttp.client", "aiohttp.access"
    ]:
        logging.getLogger(name).setLevel(logging.WARNING)
        logging.getLogger(name).propagate = False

    # 4) optional console
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG if debug else logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    return logger, audit_logger


def audit(action: str, **kv):
    audit_logger.info("\t".join([f"action={action}"] + [f"{k}={v}" for k, v in kv.items()]))


# links
logger, audit_logger = configure_logging(console=False, debug=False)
