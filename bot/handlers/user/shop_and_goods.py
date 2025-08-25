from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.database.methods import (
    get_all_categories, get_all_items, select_bought_items, get_bought_item_info, get_item_info,
    select_item_values_amount, check_value
)
from bot.keyboards import paginated_keyboard, item_info, back
from bot.i18n import localize
from bot.misc import EnvKeys
from bot.states import ShopStates

router = Router()


# --- Open shop (categories)
@router.callback_query(F.data == "shop")
async def shop_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Show list of shop categories.
    """
    categories = get_all_categories()
    markup = paginated_keyboard(
        items=categories,
        item_text=lambda cat: cat,
        item_callback=lambda cat: f"category_{cat}",
        page=0,
        per_page=10,
        back_cb="back_to_menu",
        nav_cb_prefix="categories-page_",
    )
    await call.message.edit_text(localize("shop.categories.title"), reply_markup=markup)
    await state.set_state(ShopStates.viewing_categories)


# --- Categories pagination — stateless
@router.callback_query(F.data.startswith('categories-page_'))
async def navigate_categories(call: CallbackQuery):
    """
    Pagination across shop categories.
    Format: categories-page_{page}
    """
    parts = call.data.split('_', 1)
    current_index = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0

    categories = get_all_categories() or []
    per_page = 10
    max_page = max((len(categories) - 1) // per_page, 0)
    current_index = max(0, min(current_index, max_page))

    markup = paginated_keyboard(
        items=categories,
        item_text=lambda cat: cat,
        item_callback=lambda cat: f"category_{cat}",
        page=current_index,
        per_page=per_page,
        back_cb="back_to_menu",
        nav_cb_prefix="categories-page_"
    )
    await call.message.edit_text(localize('shop.categories.title'), reply_markup=markup)


# --- Open items of a category — stateless
@router.callback_query(F.data.startswith('category_'))
async def items_list_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Show items of selected category.
    """
    category_name = call.data[9:]
    goods = get_all_items(category_name)
    markup = paginated_keyboard(
        items=goods,
        item_text=lambda item: item,
        item_callback=lambda item: f"item_{item}",
        page=0,
        per_page=10,
        back_cb="shop",
        nav_cb_prefix=f"goods-page_{category_name}_",
    )
    await call.message.edit_text(localize("shop.goods.choose"), reply_markup=markup)
    await state.set_state(ShopStates.viewing_goods)


# --- Items pagination inside a category
@router.callback_query(F.data.startswith('goods-page_'), ShopStates.viewing_goods)
async def navigate_goods(call: CallbackQuery):
    """
    Pagination for items inside selected category.
    Format: goods-page_{category}_{page}
    """
    prefix = "goods-page_"
    tail = call.data[len(prefix):]  # "{category_name}_{page}"
    category_name, current_index = tail.rsplit("_", 1)  # rsplit handles '_' inside category
    current_index = int(current_index)

    goods = get_all_items(category_name)
    markup = paginated_keyboard(
        items=goods,
        item_text=lambda item: item,
        item_callback=lambda item: f"item_{item}",
        page=current_index,
        per_page=10,
        back_cb="shop",
        nav_cb_prefix=f"goods-page_{category_name}_",
    )
    await call.message.edit_text(localize("shop.goods.choose"), reply_markup=markup)


# --- Item card — stateless (so "Back" always works to reopen it)
@router.callback_query(F.data.startswith('item_'))
async def item_info_callback_handler(call: CallbackQuery):
    """
    Show detailed information about the item.
    """
    item_name = call.data[5:]
    item_info_list = get_item_info(item_name)
    if not item_info_list:
        await call.answer(localize("shop.item.not_found"), show_alert=True)
        return

    category = item_info_list['category_name']
    quantity_line = (
        localize("shop.item.quantity_unlimited")
        if check_value(item_name)
        else localize("shop.item.quantity_left", count=select_item_values_amount(item_name))
    )
    markup = item_info(item_name, category)
    await call.message.edit_text(
        "\n".join([
            localize("shop.item.title", name=item_name),
            localize("shop.item.description", description=item_info_list["description"]),
            localize("shop.item.price", amount=item_info_list["price"], currency=EnvKeys.PAY_CURRENCY),
            quantity_line,
        ]),
        reply_markup=markup,
    )


# --- User's purchased items
@router.callback_query(F.data == "bought_items")
async def bought_items_callback_handler(call: CallbackQuery):
    """
    Show list of user's purchased items (with pagination).
    """
    user_id = call.from_user.id
    bought_goods = select_bought_items(user_id) or []

    markup = paginated_keyboard(
        items=bought_goods,
        item_text=lambda item: item.item_name,
        item_callback=lambda item: f"bought-item:{item.id}:bought-goods-page_user_0",
        page=0,
        per_page=10,
        back_cb="profile",
        nav_cb_prefix="bought-goods-page_user_"
    )
    await call.message.edit_text(localize("purchases.title"), reply_markup=markup)


# --- Purchased items pagination
@router.callback_query(F.data.startswith('bought-goods-page_'))
async def navigate_bought_items(call: CallbackQuery):
    """
    Pagination for user's purchased items.
    Format: 'bought-goods-page_{data}_{page}', where data = 'user' or user_id.
    """
    parts = call.data.split('_')
    if len(parts) < 3:
        await call.answer(localize("purchases.pagination.invalid"))
        return

    data = parts[1]
    try:
        current_index = int(parts[2])
    except ValueError:
        current_index = 0

    if data == 'user':
        user_id = call.from_user.id
        back_cb = 'profile'
        pre_back = f'bought-goods-page_user_{current_index}'
    else:
        user_id = int(data)
        back_cb = f'check-user_{data}'
        pre_back = f'bought-goods-page_{data}_{current_index}'

    bought_goods = select_bought_items(user_id) or []

    per_page = 10
    max_page = max((len(bought_goods) - 1) // per_page, 0)
    current_index = max(0, min(current_index, max_page))

    markup = paginated_keyboard(
        items=bought_goods,
        item_text=lambda item: item.item_name,
        item_callback=lambda item: f"bought-item:{item.id}:{pre_back}",
        page=current_index,
        per_page=per_page,
        back_cb=back_cb,
        nav_cb_prefix=f"bought-goods-page_{data}_"
    )
    await call.message.edit_text(localize("purchases.title"), reply_markup=markup)


# --- Purchased item details
@router.callback_query(F.data.startswith('bought-item:'))
async def bought_item_info_callback_handler(call: CallbackQuery):
    """
    Show details for a purchased item.
    """
    trash, item_id, back_data = call.data.split(':', 2)
    item = get_bought_item_info(item_id)
    if not item:
        await call.answer(localize("purchases.item.not_found"), show_alert=True)
        return

    text = "\n".join([
        localize("purchases.item.name", name=item["item_name"]),
        localize("purchases.item.price", amount=item["price"], currency=EnvKeys.PAY_CURRENCY),
        localize("purchases.item.datetime", dt=item["bought_datetime"]),
        localize("purchases.item.unique_id", uid=item["unique_id"]),
        localize("purchases.item.value", value=item["value"]),
    ])
    await call.message.edit_text(text, parse_mode='HTML', reply_markup=back(back_data))
