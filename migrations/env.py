from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool

import bot.database.models.main  # noqa: F401
from bot.database.main import Database
from bot.database.dsn import dsn

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Database.BASE.metadata


def get_url() -> str:
    url = dsn()
    return url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    if config:
        config.set_main_option("sqlalchemy.url", url)

    connectable = create_engine(dsn(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
