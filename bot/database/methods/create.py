from datetime import datetime
import random
from decimal import Decimal

from sqlalchemy import exists
from sqlalchemy.exc import IntegrityError

from bot.database.models import (
    User, ItemValues, Goods, Categories, BoughtGoods, Operations, Payments
)
from bot.database import Database


def create_user(telegram_id: int, registration_date: datetime, referral_id: int | str, role: int = 1) -> None:
    """Create user if missing; commit."""
    with Database().session() as s:
        if s.query(exists().where(User.telegram_id == telegram_id)).scalar():
            return
        s.add(
            User(
                telegram_id=telegram_id,
                role_id=role,
                registration_date=registration_date,
                referral_id=None if referral_id in ("", None) else referral_id,
            )
        )


def create_item(item_name: str, item_description: str, item_price: int, category_name: str) -> None:
    """Insert item (goods); commit."""
    with Database().session() as s:
        if s.query(exists().where(Goods.name == item_name)).scalar():
            return
        s.add(
            Goods(
                name=item_name,
                description=item_description,
                price=item_price,
                category_name=category_name,
            )
        )


def add_values_to_item(item_name: str, value: str, is_infinity: bool) -> bool:
    """Add item value if not duplicate; True if inserted."""
    value_norm = (value or "").strip()
    if not value_norm:
        return False

    with Database().session() as s:
        if s.query(
                exists().where(
                    ItemValues.item_name == item_name,
                    ItemValues.value == value_norm
                )
        ).scalar():
            return False

        try:
            s.add(ItemValues(name=item_name, value=value_norm, is_infinity=bool(is_infinity)))
            return True
        except IntegrityError:
            return False


def create_category(category_name: str) -> None:
    """Insert category; commit."""
    with Database().session() as s:
        if s.query(exists().where(Categories.name == category_name)).scalar():
            return
        s.add(Categories(name=category_name))


def create_operation(user_id: int, value: int, operation_time: datetime) -> None:
    """Record completed balance operation; commit."""
    with Database().session() as s:
        s.add(Operations(user_id, value, operation_time))


def add_bought_item(item_name: str, value: str, price: int, buyer_id: int, bought_time: datetime) -> None:
    """Record purchase (bought item); commit."""
    with Database().session() as s:
        s.add(
            BoughtGoods(
                name=item_name,
                value=value,
                price=price,
                buyer_id=buyer_id,
                bought_datetime=bought_time,
                unique_id=str(random.randint(1_000_000_000, 9_999_999_999)),
            )
        )


def create_pending_payment(provider: str, external_id: str, user_id: int, amount: int, currency: str) -> None:
    """Create pending payment."""
    with Database().session() as s:
        s.add(Payments(
            provider=provider,
            external_id=external_id,
            user_id=user_id,
            amount=Decimal(amount),
            currency=currency,
            status="pending"
        ))
