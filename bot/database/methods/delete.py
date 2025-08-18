from bot.database.models import Database, Goods, ItemValues, Categories


def delete_item(item_name: str) -> None:
    """Delete a product and all of its stock entries.
    Removes the Goods row by name and all related ItemValues, then commits.
    No error is raised if nothing matches.
    """
    Database().session.query(Goods).filter(Goods.name == item_name).delete()
    Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).delete()
    Database().session.commit()


def delete_item_from_position(item_id: int) -> None:
    """Delete a single stock row by its ItemValues id, then commit.
    """
    Database().session.query(ItemValues).filter(ItemValues.id == item_id).delete()
    Database().session.commit()


def delete_only_items(item_name: str) -> None:
    """Delete all stock entries (ItemValues) for a product, keep Goods row.
    """
    Database().session.query(ItemValues).filter(ItemValues.item_name == item_name).delete()
    Database().session.commit()


def delete_category(category_name: str) -> None:
    """Delete a category and all products/stock inside it.
    Deletes ItemValues for products in the category, then Goods of that
    category, then the Categories row. Commits at the end.
    """
    goods = Database().session.query(Goods.name).filter(Goods.category_name == category_name).all()
    for item in goods:
        Database().session.query(ItemValues).filter(ItemValues.item_name == item.name).delete()
    Database().session.query(Goods).filter(Goods.category_name == category_name).delete()
    Database().session.query(Categories).filter(Categories.name == category_name).delete()
    Database().session.commit()


def buy_item(item_id: str, infinity: bool = False) -> None:
    """Consume one stock entry after purchase (unless item is infinite).
    If `infinity` is False: delete ItemValues by id and commit.
    If `infinity` is True: do nothing.
    """
    if not infinity:
        Database().session.query(ItemValues).filter(ItemValues.id == item_id).delete()
        Database().session.commit()
    else:
        pass
