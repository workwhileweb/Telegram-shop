from sqlalchemy import exc
from sqlalchemy.orm import Session

from bot.database.models import User, ItemValues, Goods, Categories, BoughtGoods
from bot.database import Database


def set_role(telegram_id: int, role: int) -> None:
    Database().session.query(User).filter(User.telegram_id == telegram_id).update(
        values={User.role_id: role})
    Database().session.commit()


def update_balance(telegram_id: int | str, summ: int) -> None:
    Database().session.query(User).filter(User.telegram_id == telegram_id).update(
        {User.balance: User.balance + summ}
    )
    Database().session.commit()


def buy_item_for_balance(telegram_id: int, summ: int) -> int:
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
    Обновляет позицию. Если меняется name (PK), делаем «переезд»:
      1) создаём новую Goods(new_name)
      2) обновляем ссылки у ItemValues (+при желании BoughtGoods)
      3) удаляем старую Goods(old_name)
    Возвращает (ok, error_message).
    """
    session: Session = Database().session
    try:
        goods = session.query(Goods).filter(Goods.name == item_name).one_or_none()
        if not goods:
            return False, "Позиция не найдена."

        # Если имя не меняется — обновляем поля напрямую
        if new_name == item_name:
            goods.description = description
            goods.price = price
            goods.category_name = category
            session.commit()
            return True, None

        # Имя меняется — проверим, что нового имени ещё нет
        if session.query(Goods).filter(Goods.name == new_name).first():
            return False, "Позиция с таким именем уже существует."

        # 1) создаём новую запись с новым именем
        new_goods = Goods(name=new_name, price=price, description=description, category_name=category)
        session.add(new_goods)
        session.flush()  # чтобы PK/уникальные проверки отработали

        # 2) перевешиваем детей
        session.query(ItemValues).filter(ItemValues.item_name == item_name) \
            .update({ItemValues.item_name: new_name}, synchronize_session=False)

        # Если хотите, чтобы история покупок тоже переименовывалась:
        session.query(BoughtGoods).filter(BoughtGoods.item_name == item_name) \
            .update({BoughtGoods.item_name: new_name}, synchronize_session=False)

        # 3) удаляем старую запись
        session.query(Goods).filter(Goods.name == item_name).delete(synchronize_session=False)

        session.commit()
        return True, None

    except exc.SQLAlchemyError as e:
        session.rollback()
        return False, f"Ошибка БД: {e.__class__.__name__}"


def update_category(category_name: str, new_name: str) -> None:
    Database().session.query(Goods).filter(Goods.category_name == category_name).update(
        values={Goods.category_name: new_name})
    Database().session.query(Categories).filter(Categories.name == category_name).update(
        values={Categories.name: new_name})
    Database().session.commit()
