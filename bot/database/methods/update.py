from sqlalchemy import exc, update, insert
from sqlalchemy.exc import IntegrityError

from bot.database.models import User, ItemValues, Goods, Categories, BoughtGoods, Payments
from bot.database import Database
from bot.i18n import localize


def set_role(telegram_id: int, role: int) -> None:
    """Set user's role (by Telegram ID) and commit."""
    with Database().session() as s:
        s.query(User).filter(User.telegram_id == telegram_id).update(
            {User.role_id: role}
        )


def update_balance(telegram_id: int | str, summ: int) -> None:
    """Increase user's balance by `summ` and commit."""
    with Database().session() as s:
        s.query(User).filter(User.telegram_id == telegram_id).update(
            {User.balance: User.balance + summ}
        )


def buy_item_for_balance(telegram_id: int, summ: int) -> int:
    """Deduct `summ` from user balance and return the new balance."""
    with Database().session() as s:
        res = s.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(balance=User.balance - summ)
            .returning(User.balance)
        )
        return int(res.scalar_one())


def update_item(item_name: str, new_name: str, description: str, price, category: str) -> tuple[bool, str | None]:
    """
    Update a Goods record. If the primary key (name) changes, perform a safe rename:
    create a new row, re-link children (ItemValues, BoughtGoods), delete the old row.
    Returns (ok, error_message).
    """
    try:
        with Database().session() as session:
            goods = session.query(Goods).filter(Goods.name == item_name).one_or_none()
            if not goods:
                return False, localize("admin.goods.update.position.invalid")

            if new_name == item_name:
                goods.description = description
                goods.price = price
                goods.category_name = category
                return True, None

            if session.query(Goods).filter(Goods.name == new_name).first():
                return False, localize("admin.goods.update.position.exists")

            new_goods = Goods(name=new_name, price=price, description=description, category_name=category)
            session.add(new_goods)
            session.flush()

            session.query(ItemValues).filter(ItemValues.item_name == item_name) \
                .update({ItemValues.item_name: new_name}, synchronize_session=False)

            session.query(BoughtGoods).filter(BoughtGoods.item_name == item_name) \
                .update({BoughtGoods.item_name: new_name}, synchronize_session=False)

            session.query(Goods).filter(Goods.name == item_name).delete(synchronize_session=False)

            return True, None

    except exc.SQLAlchemyError as e:
        return False, f"DB Error: {e.__class__.__name__}"


def update_category(category_name: str, new_name: str) -> None:
    """Rename a category and cascade the change into Goods.category_name."""
    with Database().session() as s:
        s.query(Goods).filter(Goods.category_name == category_name).update(
            {Goods.category_name: new_name}
        )
        s.query(Categories).filter(Categories.name == category_name).update(
            {Categories.name: new_name}
        )


def mark_payment_succeeded(provider: str, external_id: str) -> bool:
    with Database().session() as s:
        row = s.query(Payments).filter(
            Payments.provider == provider,
            Payments.external_id == external_id
        ).with_for_update(nowait=True).one_or_none()
        if not row:
            return False
        if row.status == "succeeded":
            return False
        row.status = "succeeded"
        return True


def ensure_payment_succeeded(provider: str, external_id: str, user_id: int, amount: int, currency: str) -> str:
    """
    Changes the payment status to 'succeeded'.
    Returns: 'created' (new record), 'updated' (from pending to succeeded), 'already' (already succeeded).
    """
    with Database().session() as s:
        row = s.execute(
            update(Payments)
            .where(
                Payments.provider == provider,
                Payments.external_id == external_id,
                Payments.status != "succeeded",
            )
            .values(status="succeeded")
            .returning(Payments.id)
        ).first()
        if row:
            return "updated"

        try:
            s.execute(
                insert(Payments).values(
                    provider=provider,
                    external_id=external_id,
                    user_id=user_id,
                    amount=amount,
                    currency=currency,
                    status="succeeded",
                )
            )
            return "created"
        except IntegrityError:
            return "already"
