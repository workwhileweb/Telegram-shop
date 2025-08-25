from bot.database.models import Database, Goods, ItemValues, Categories


def delete_item(item_name: str) -> None:
    """Delete a product and all of its stock entries.
    Removes the Goods row by name and all related ItemValues, then commits.
    No error is raised if nothing matches.
    """
    with Database().session() as s:
        s.query(Goods).filter(Goods.name == item_name).delete(synchronize_session=False)


def delete_only_items(item_name: str) -> None:
    """Delete all stock entries (ItemValues) for a product, keep Goods row."""
    with Database().session() as s:
        s.query(ItemValues).filter(ItemValues.item_name == item_name).delete(synchronize_session=False)


def delete_item_from_position(item_id: int) -> None:
    """Delete a single stock row by its ItemValues id."""
    with Database().session() as s:
        s.query(ItemValues).filter(ItemValues.id == item_id).delete(synchronize_session=False)


def delete_category(category_name: str) -> None:
    """Delete a category and all products/stock inside it.
    Deletes ItemValues for products in the category, then Goods of that
    category, then the Categories row. Commits at the end.
    """
    with Database().session() as s:
        s.query(Categories).filter(Categories.name == category_name).delete(synchronize_session=False)


def buy_item(item_id: str, infinity: bool = False) -> None:
    """Consume one stock entry after purchase (unless item is infinite)."""
    if not infinity:
        with Database().session() as s:
            s.query(ItemValues).filter(ItemValues.id == item_id).delete(synchronize_session=False)
