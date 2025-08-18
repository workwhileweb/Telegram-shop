import sqlite3
from typing import Final
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bot.misc import SingletonMeta


def _sqlite_fk_on_connect(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")


class Database(metaclass=SingletonMeta):
    BASE: Final = declarative_base()

    def __init__(self):
        self.__engine = create_engine(f'sqlite:///database.db', echo=False, pool_pre_ping=True)
        if self.__engine.dialect.name == "sqlite":
            event.listen(self.__engine, "connect", _sqlite_fk_on_connect)
        session = sessionmaker(bind=self.__engine)
        self.__session = session()

    @property
    def session(self):
        return self.__session

    @property
    def engine(self):
        return self.__engine
