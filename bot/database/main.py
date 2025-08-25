from contextlib import contextmanager
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bot.database.dsn import dsn
from bot.misc import SingletonMeta


class Database(metaclass=SingletonMeta):
    BASE = declarative_base()

    def __init__(self):
        self.__engine: Engine = create_engine(
            dsn(),
            echo=False,
            pool_pre_ping=True,
            future=True,
        )
        self.__SessionLocal = sessionmaker(bind=self.__engine, autoflush=False, autocommit=False, future=True,
                                           expire_on_commit=False)

    @contextmanager
    def session(self):
        """Contextual session: guaranteed to close/rollback on error."""
        db = self.__SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @property
    def engine(self) -> Engine:
        return self.__engine
