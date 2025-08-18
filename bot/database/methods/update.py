from sqlalchemy import exc
from sqlalchemy.orm import Session

from bot.database.models import User, ItemValues, Goods, Categories, BoughtGoods
from bot.database import Database
from bot.i18n import localize


def set_role(telegram_id: int, role: int) -> None:
    """Set user's role (by Telegram ID) and commit."""
    Database().session.query(User).filter(User.telegram_id == telegram_id).update(
        values={User.role_id: role})
    Database().session.commit()


def update_balance(telegram_id: int | str, summ: int) -> None:
    """Increase user's balance by `summ` and commit."""
    Database().session.query(User).filter(User.telegram_id == telegram_id).update(
        {User.balance: User.balance + summ}
    )
    Database().session.commit()


def buy_item_for_balance(telegram_id: int, summ: int) -> int:
    """Deduct `summ` from user balance and return the new balance."""
    Database().session.query(User).filter(User.telegram_id == telegram_id).update(
        {User.balance: User.balance - summ}
    )
    Database().session.commit()
    return (
        Database()
        .session.query(User.balance)
        .filter(User.telegram_id == telegram_id)
        .one()[0]
    )


def update_item(item_name: str, new_name: str, description: str, price, category: str) -> tuple[bool, str | None]:
    """
    Update a Goods record. If the primary key (name) changes, perform a safe rename:
    create a new row, re-link children (ItemValues, BoughtGoods), delete the old row.
    Returns (ok, error_message).
    """
    session: Session = Database().session
    try:
        goods = session.query(Goods).filter(Goods.name == item_name).one_or_none()
        if not goods:
            return False, localize("admin.goods.update.position.invalid")

        # No PK change: patch fields directly.
        if new_name == item_name:
            goods.description = description
            goods.price = price
            goods.category_name = category
            session.commit()
            return True, None

        # PK change: ensure new name is free.
        if session.query(Goods).filter(Goods.name == new_name).first():
            return False, localize("admin.goods.update.position.exists")

        # 1) Create new row under the new name.
        new_goods = Goods(name=new_name, price=price, description=description, category_name=category)
        session.add(new_goods)
        session.flush()

        # 2) Re-point children.
        session.query(ItemValues).filter(ItemValues.item_name == item_name) \
            .update({ItemValues.item_name: new_name}, synchronize_session=False)

        session.query(BoughtGoods).filter(BoughtGoods.item_name == item_name) \
            .update({BoughtGoods.item_name: new_name}, synchronize_session=False)

        # 3) Delete old row.
        session.query(Goods).filter(Goods.name == item_name).delete(synchronize_session=False)

        session.commit()
        return True, None

    except exc.SQLAlchemyError as e:
        session.rollback()
        return False, f"DB Error: {e.__class__.__name__}"


def update_category(category_name: str, new_name: str) -> None:
    """Rename a category and cascade the change into Goods.category_name."""
    Database().session.query(Goods).filter(Goods.category_name == category_name).update(
        values={Goods.category_name: new_name})
    Database().session.query(Categories).filter(Categories.name == category_name).update(
        values={Categories.name: new_name})
    Database().session.commit()
