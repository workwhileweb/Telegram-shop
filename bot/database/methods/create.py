from datetime import datetime
import random
import sqlalchemy.exc
from sqlalchemy.exc import IntegrityError

from bot.database.models import (
    User, ItemValues, Goods, Categories, BoughtGoods, Operations
)
from bot.database import Database


def create_user(telegram_id: int, registration_date: datetime, referral_id: int | str, role: int = 1) -> None:
    """Create user if missing; commit."""
    session = Database().session
    try:
        session.query(User.telegram_id).filter(User.telegram_id == telegram_id).one()
    except sqlalchemy.exc.NoResultFound:
        session.add(
            User(
                telegram_id=telegram_id,
                role_id=role,
                registration_date=registration_date,
                referral_id=None if referral_id == '' else referral_id,
            )
        )
        session.commit()


def create_item(item_name: str, item_description: str, item_price: int, category_name: str) -> None:
    """Insert item (goods); commit."""
    session = Database().session
    session.add(
        Goods(
            name=item_name,
            description=item_description,
            price=item_price,
            category_name=category_name,
        )
    )
    session.commit()


def add_values_to_item(item_name: str, value: str, is_infinity: bool) -> bool:
    """Add item value if not duplicate; True if inserted."""
    session = Database().session
    value_norm = (value or "").strip()
    if not value_norm:
        return False

    exists = session.query(ItemValues.id).filter(
        ItemValues.item_name == item_name,
        ItemValues.value == value_norm
    ).first()
    if exists:
        return False

    try:
        session.add(ItemValues(name=item_name, value=value_norm, is_infinity=is_infinity))
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def create_category(category_name: str) -> None:
    """Insert category; commit."""
    session = Database().session
    session.add(Categories(name=category_name))
    session.commit()


def create_operation(user_id: int, value: int, operation_time: datetime) -> None:
    """Record completed balance operation; commit."""
    session = Database().session
    session.add(
        Operations(
            user_id=user_id,
            operation_value=value,
            operation_time=operation_time,
        )
    )
    session.commit()


def add_bought_item(item_name: str, value: str, price: int, buyer_id: int, bought_time: datetime) -> None:
    """Record purchase (bought item); commit."""
    session = Database().session
    session.add(
        BoughtGoods(
            name=item_name,
            value=value,
            price=price,
            buyer_id=buyer_id,
            bought_datetime=bought_time,
            unique_id=str(random.randint(1000000000, 9999999999)),
        )
    )
    session.commit()
