import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from bot.misc import EnvKeys

LOG_PATH = EnvKeys.BOT_LOGFILE
AUDIT_PATH = EnvKeys.BOT_AUDITFILE


def configure_logging(console: bool = False, debug: bool = False) -> tuple[logging.Logger, logging.Logger]:
    """
    Настраивает логирование проекта:
    - прикладной логгер "telegram_shop" -> файл (UTF-8, ротация)
    - отдельный audit-логгер "telegram_shop.audit" -> файл (UTF-8, по дням)
    """
    # 0) root — без хендлеров и на WARNING
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(logging.WARNING)

    # 1) основной логгер
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

    # 2) audit-логгер — только важные действия (создание товара, смена ролей и т.п.)
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

    # 3) приглушаем внешние логгеры
    for name in [
        "aiogram", "aiogram.event", "aiogram.dispatcher", "aiogram.client", "aiohttp", "aiogram.client.telegram",
        "aiogram.client.session.aiohttp", "aiohttp.client", "aiohttp.access"
    ]:
        logging.getLogger(name).setLevel(logging.WARNING)
        logging.getLogger(name).propagate = False

    # 4) опционально консоль
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG if debug else logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    return logger, audit_logger


def audit(action: str, **kv):
    audit_logger.info("\t".join([f"action={action}"] + [f"{k}={v}" for k, v in kv.items()]))


# Ссылки
logger, audit_logger = configure_logging(console=False, debug=False)
