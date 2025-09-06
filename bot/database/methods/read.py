import datetime
from decimal import Decimal
from typing import Optional, List, Dict

from sqlalchemy import func, exists, desc

from bot.database.models import Database, User, ItemValues, Goods, Categories, Role, BoughtGoods, \
    Operations, ReferralEarnings


def _day_window(date_str: str) -> tuple[datetime.datetime, datetime.datetime]:
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    start = datetime.datetime.combine(d, datetime.time.min)
    end = start + datetime.timedelta(days=1)
    return start, end


def check_user(telegram_id: int | str) -> Optional[User]:
    """Return user by Telegram ID or None if not found."""
    with Database().session() as s:
        return s.query(User).filter(User.telegram_id == telegram_id).one_or_none()


def check_role(telegram_id: int) -> int:
    """Return permission bitmask for user (0 if none)."""
    with Database().session() as s:
        role_id = s.query(User.role_id).filter(User.telegram_id == telegram_id).scalar()
        if not role_id:
            return 0
        perms = s.query(Role.permissions).filter(Role.id == role_id).scalar()
        return perms or 0


def get_role_id_by_name(role_name: str) -> Optional[int]:
    """Return role id by name or None."""
    with Database().session() as s:
        return s.query(Role.id).filter(Role.name == role_name).scalar()


def check_role_name_by_id(role_id: int) -> str:
    """Return role name by id (raises if not found)."""
    with Database().session() as s:
        return s.query(Role.name).filter(Role.id == role_id).one()[0]


def select_max_role_id() -> Optional[int]:
    """Return max role id (or None if no roles)."""
    with Database().session() as s:
        return s.query(func.max(Role.id)).scalar()


def select_today_users(date: str) -> int:
    """Return count of users registered on given date (YYYY-MM-DD)."""
    start_of_day, end_of_day = _day_window(date)
    with Database().session() as s:
        return s.query(User).filter(
            User.registration_date >= start_of_day,
            User.registration_date < end_of_day
        ).count()


def get_user_count() -> int:
    """Return total users count."""
    with Database().session() as s:
        return s.query(User).count()


def select_admins() -> int:
    """Return count of users with role_id > 1."""
    with Database().session() as s:
        return s.query(func.count(User.telegram_id)).filter(User.role_id > 1).scalar() or 0


def get_all_users() -> list[tuple[int]]:
    """Return list of all user telegram_ids (as tuples)."""
    with Database().session() as s:
        return s.query(User.telegram_id).all()


def get_bought_item_info(item_id: str) -> dict | None:
    """Return bought item row as dict by row id, or None."""
    with Database().session() as s:
        result = s.query(BoughtGoods).filter(BoughtGoods.id == item_id).first()
        return result.__dict__ if result else None


def get_item_info(item_name: str) -> dict | None:
    """Return item (position) row as dict by name, or None."""
    with Database().session() as s:
        result = s.query(Goods).filter(Goods.name == item_name).first()
        return result.__dict__ if result else None


def get_goods_info(item_id: int) -> dict | None:
    """Return item_value row as dict by id, or None."""
    with Database().session() as s:
        result = s.query(ItemValues).filter(ItemValues.id == int(item_id)).first()
        return result.__dict__ if result else None


def check_item(item_name: str) -> dict | None:
    """Return item (position) as dict by name, or None."""
    with Database().session() as s:
        result = s.query(Goods).filter(Goods.name == item_name).first()
        return result.__dict__ if result else None


def check_category(category_name: str) -> dict | None:
    """Return category as dict by name, or None."""
    with Database().session() as s:
        result = s.query(Categories).filter(Categories.name == category_name).first()
        return result.__dict__ if result else None


def select_item_values_amount(item_name: str) -> int:
    """Return count of item_values for an item."""
    with Database().session() as s:
        return s.query(func.count()).filter(ItemValues.item_name == item_name).scalar() or 0


def check_value(item_name: str) -> bool:
    """Return True if item has any infinite value (is_infinity=True)."""
    with Database().session() as s:
        return s.query(
            exists().where(
                ItemValues.item_name == item_name,
                ItemValues.is_infinity.is_(True),
            )
        ).scalar()


def select_user_items(buyer_id: int | str) -> int:
    """Return count of bought items for user."""
    with Database().session() as s:
        return s.query(func.count()).filter(BoughtGoods.buyer_id == buyer_id).scalar() or 0


def select_bought_item(unique_id: int) -> dict | None:
    """Return one bought item by unique_id as dict, or None."""
    with Database().session() as s:
        result = s.query(BoughtGoods).filter(BoughtGoods.unique_id == unique_id).first()
        return result.__dict__ if result else None


def select_count_items() -> int:
    """Return total count of item_values."""
    with Database().session() as s:
        return s.query(ItemValues).count()


def select_count_goods() -> int:
    """Return total count of goods (positions)."""
    with Database().session() as s:
        return s.query(Goods).count()


def select_count_categories() -> int:
    """Return total count of categories."""
    with Database().session() as s:
        return s.query(Categories).count()


def select_count_bought_items() -> int:
    """Return total count of bought items."""
    with Database().session() as s:
        return s.query(BoughtGoods).count()


def select_today_orders(date: str) -> Decimal:
    """Return total revenue for given date (YYYY-MM-DD)."""
    start_of_day, end_of_day = _day_window(date)
    with Database().session() as s:
        res = (
            s.query(func.sum(BoughtGoods.price))
            .filter(
                BoughtGoods.bought_datetime >= start_of_day,
                BoughtGoods.bought_datetime < end_of_day
            )
            .scalar()
        )
        return res or Decimal(0)


def select_all_orders() -> Decimal:
    """Return total revenue for all time (sum of BoughtGoods.price)."""
    with Database().session() as s:
        return s.query(func.sum(BoughtGoods.price)).scalar() or Decimal(0)


def select_today_operations(date: str) -> Decimal:
    """Return total operations value for given date (YYYY-MM-DD)."""
    start_of_day, end_of_day = _day_window(date)
    with Database().session() as s:
        res = (
            s.query(func.sum(Operations.operation_value))
            .filter(
                Operations.operation_time >= start_of_day,
                Operations.operation_time < end_of_day
            )
            .scalar()
        )
        return res or Decimal(0)


def select_all_operations() -> Decimal:
    """Return total operations value for all time."""
    with Database().session() as s:
        return s.query(func.sum(Operations.operation_value)).scalar() or Decimal(0)


def select_users_balance():
    """Return sum of all users' balances."""
    with Database().session() as s:
        return s.query(func.sum(User.balance)).scalar()


def select_user_operations(user_id: int | str) -> list[float]:
    """Return list of operation amounts for user."""
    with Database().session() as s:
        return [row[0] for row in s.query(Operations.operation_value).filter(Operations.user_id == user_id).all()]


def check_user_referrals(user_id: int) -> int:
    """Return count of referrals of the user."""
    with Database().session() as s:
        return s.query(User).filter(User.referral_id == user_id).count()


def get_user_referral(user_id: int) -> Optional[int]:
    """Return referral_id of the user or None."""
    with Database().session() as s:
        result = s.query(User.referral_id).filter(User.telegram_id == user_id).first()
        return result[0] if result else None


def get_referral_earnings_stats(referrer_id: int) -> Dict:
    """
    Get statistics on user referral charges.
    """
    with Database().session() as s:
        stats = s.query(
            func.count(ReferralEarnings.id).label('total_earnings_count'),
            func.sum(ReferralEarnings.amount).label('total_amount'),
            func.sum(ReferralEarnings.original_amount).label('total_original_amount'),
            func.count(func.distinct(ReferralEarnings.referral_id)).label('active_referrals_count')
        ).filter(
            ReferralEarnings.referrer_id == referrer_id
        ).first()

        return {
            'total_earnings_count': stats.total_earnings_count or 0,
            'total_amount': stats.total_amount or Decimal(0),
            'total_original_amount': stats.total_original_amount or Decimal(0),
            'active_referrals_count': stats.active_referrals_count or 0
        }


def get_one_referral_earning(earning_id: int) -> dict | None:
    """
    Get one user referral earning info.
    """
    with Database().session() as s:
        result = s.query(ReferralEarnings).filter(ReferralEarnings.id == earning_id).first()
        return result.__dict__ if result else None
