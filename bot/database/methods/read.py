import datetime
from decimal import Decimal
from sqlalchemy import exc, func

from bot.database.models import Database, User, ItemValues, Goods, Categories, Role, BoughtGoods, \
    Operations


def check_user(telegram_id: int | str) -> User | None:
    """Return user by Telegram ID or None if not found."""
    try:
        return Database().session.query(User).filter(User.telegram_id == telegram_id).one()
    except exc.NoResultFound:
        return None


def check_role(telegram_id: int) -> int | None:
    """Return permission bitmask for user (0 if none)."""
    role_id = Database().session.query(User.role_id).filter(User.telegram_id == telegram_id).scalar()
    if not role_id:
        return 0
    perms = Database().session.query(Role.permissions).filter(Role.id == role_id).scalar()
    return perms or 0


def get_role_id_by_name(role_name: str) -> int | None:
    """Return role id by name or None."""
    return Database().session.query(Role.id).filter(Role.name == role_name).scalar()


def check_role_name_by_id(role_id: int):
    """Return role name by id (raises if not found)."""
    return Database().session.query(Role.name).filter(Role.id == role_id).one()[0]


def select_max_role_id() -> int:
    """Return max role id (or None if no roles)."""
    return Database().session.query(func.max(Role.id)).scalar()


def select_today_users(date: str) -> int | None:
    """Return count of users registered on given date (YYYY-MM-DD)."""
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start_of_day = datetime.datetime.combine(date_obj, datetime.time.min)
        end_of_day = datetime.datetime.combine(date_obj, datetime.time.max)

        return Database().session.query(User).filter(
            User.registration_date >= start_of_day,
            User.registration_date <= end_of_day
        ).count()
    except exc.NoResultFound:
        return None


def get_user_count() -> int:
    """Return total users count."""
    return Database().session.query(User).count()


def select_admins() -> int | None:
    """Return count of users with role_id > 1."""
    try:
        return Database().session.query(func.count()).filter(User.role_id > 1).scalar()
    except exc.NoResultFound:
        return None


def get_all_users() -> list[tuple[int]]:
    """Return list of all user telegram_ids (as tuples)."""
    return Database().session.query(User.telegram_id).all()


def get_all_categories() -> list[str]:
    """Return list of all category names."""
    return [category[0] for category in Database().session.query(Categories.name).all()]


def get_all_items(category_name: str) -> list[str]:
    """Return all item (position) names for a category."""
    return [item[0] for item in
            Database().session.query(Goods.name).filter(Goods.category_name == category_name).all()]


def select_items(item_name: str) -> list[int]:
    """Return list of item_value ids for given item (position) name."""
    return [item[0] for item in
            Database().session.query(ItemValues.id).join(Goods).filter(Goods.name == item_name).all()]


def get_bought_item_info(item_id: str) -> dict | None:
    """Return bought item row as dict by row id, or None."""
    result = Database().session.query(BoughtGoods).filter(BoughtGoods.id == item_id).first()
    return result.__dict__ if result else None


def get_item_info(item_name: str) -> dict | None:
    """Return item (position) row as dict by name, or None."""
    result = Database().session.query(Goods).filter(Goods.name == item_name).first()
    return result.__dict__ if result else None


def get_goods_info(item_id: int) -> dict | None:
    """Return item_value row as dict by id, or None."""
    result = Database().session.query(ItemValues).filter(ItemValues.id == int(item_id)).first()
    return result.__dict__ if result else None


def get_user_balance(telegram_id: int):
    """Return user's balance (Decimal), or 0 if missing."""
    result = Database().session.query(User.balance).filter(User.telegram_id == telegram_id).first()
    return result[0] if result else Decimal(0)


def get_all_admins() -> list[int]:
    """Return list of telegram_ids of users with ADMIN role."""
    return [admin[0] for admin in
            Database().session.query(User.telegram_id).join(Role).filter(Role.name == 'ADMIN').all()]


def check_item(item_name: str) -> dict | None:
    """Return item (position) as dict by name, or None."""
    result = Database().session.query(Goods).filter(Goods.name == item_name).first()
    return result.__dict__ if result else None


def check_category(category_name: str) -> dict | None:
    """Return category as dict by name, or None."""
    result = Database().session.query(Categories).filter(Categories.name == category_name).first()
    return result.__dict__ if result else None


def get_item_value(item_name: str) -> dict | None:
    """Return first item_value of item by name as dict, or None."""
    result = Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).first()
    return result.__dict__ if result else None


def select_item_values_amount(item_name: str) -> int:
    """Return count of item_values for an item."""
    return Database().session.query(func.count()).filter(ItemValues.item_name == item_name).scalar()


def check_value(item_name: str) -> bool | None:
    """Return True if item has any infinite value (is_infinity=True)."""
    try:
        result = False
        values = select_item_values_amount(item_name)
        for i in range(values):
            is_inf = Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).first()
            if is_inf and is_inf.is_infinity:
                result = True
    except exc.NoResultFound:
        return False
    return result


def select_user_items(buyer_id: int | str) -> int:
    """Return count of bought items for user."""
    return Database().session.query(func.count()).filter(BoughtGoods.buyer_id == buyer_id).scalar()


def select_bought_items(buyer_id: int) -> list[str]:
    """Return all BoughtGoods rows for user."""
    return Database().session.query(BoughtGoods).filter(BoughtGoods.buyer_id == buyer_id).all()


def select_bought_item(unique_id: int) -> dict | None:
    """Return one bought item by unique_id as dict, or None."""
    result = Database().session.query(BoughtGoods).filter(BoughtGoods.unique_id == unique_id).first()
    return result.__dict__ if result else None


def select_count_items() -> int:
    """Return total count of item_values."""
    return Database().session.query(ItemValues).count()


def select_count_goods() -> int:
    """Return total count of goods (positions)."""
    return Database().session.query(Goods).count()


def select_count_categories() -> int:
    """Return total count of categories."""
    return Database().session.query(Categories).count()


def select_count_bought_items() -> int:
    """Return total count of bought items."""
    return Database().session.query(BoughtGoods).count()


def select_today_orders(date: str) -> Decimal | None:
    """Return total revenue for given date (YYYY-MM-DD)."""
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start_of_day = datetime.datetime.combine(date_obj, datetime.time.min)
        end_of_day = datetime.datetime.combine(date_obj, datetime.time.max)

        res = (
            Database().session.query(func.sum(BoughtGoods.price))
            .filter(
                BoughtGoods.bought_datetime >= start_of_day,
                BoughtGoods.bought_datetime <= end_of_day
            )
            .scalar()
        )
        return res or Decimal(0)
    except exc.NoResultFound:
        return None


def select_all_orders() -> Decimal:
    """Return total revenue for all time (sum of BoughtGoods.price)."""
    return Database().session.query(func.sum(BoughtGoods.price)).scalar() or Decimal(0)


def select_today_operations(date: str) -> Decimal | None:
    """Return total operations value for given date (YYYY-MM-DD)."""
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start_of_day = datetime.datetime.combine(date_obj, datetime.time.min)
        end_of_day = datetime.datetime.combine(date_obj, datetime.time.max)

        res = (
            Database().session.query(func.sum(Operations.operation_value))
            .filter(
                Operations.operation_time >= start_of_day,
                Operations.operation_time <= end_of_day
            )
            .scalar()
        )
        return res or Decimal(0)
    except exc.NoResultFound:
        return None


def select_all_operations() -> Decimal:
    """Return total operations value for all time."""
    return Database().session.query(func.sum(Operations.operation_value)).scalar() or Decimal(0)


def select_users_balance() -> float:
    """Return sum of all users' balances."""
    return Database().session.query(func.sum(User.balance)).scalar()


def select_user_operations(user_id: int | str) -> list[float]:
    """Return list of operation amounts for user."""
    return [operation[0] for operation in
            Database().session.query(Operations.operation_value).filter(Operations.user_id == user_id).all()]


def check_user_referrals(user_id: int) -> list[int]:
    """Return count of referrals of the user."""
    return Database().session.query(User).filter(User.referral_id == user_id).count()


def get_user_referral(user_id: int) -> int | None:
    """Return referral_id of the user or None."""
    result = Database().session.query(User.referral_id).filter(User.telegram_id == user_id).first()
    return result[0] if result else None
