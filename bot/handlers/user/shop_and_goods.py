from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from bot.database.methods import (
    get_all_categories, get_all_items, select_bought_items, get_bought_item_info, get_item_info,
    select_item_values_amount, check_value
)
from bot.keyboards import paginated_keyboard, item_info, back

router = Router()


class ShopStates(StatesGroup):
    """
    Состояния FSM для раздела покупок (для личного списка покупок).
    """
    viewing_goods = State()
    viewing_bought_items = State()
    viewing_categories = State()


# --- Открыть магазин (категории)
@router.callback_query(F.data == "shop")
async def shop_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Показывает пользователю список категорий магазина.
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
    await call.message.edit_text("🏪 Категории магазина", reply_markup=markup)
    await state.set_state(ShopStates.viewing_categories)


# --- Пагинация категорий — БЕЗ состояния
@router.callback_query(F.data.startswith('categories-page_'))
async def navigate_categories(call: CallbackQuery):
    """
    Пагинация по списку категорий магазина.
    Формат: categories-page_{page}
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
    await call.message.edit_text('🏪 Категории магазина', reply_markup=markup)


# --- Открыть список товаров категории — БЕЗ состояния
@router.callback_query(F.data.startswith('category_'))
async def items_list_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Показывает список товаров выбранной категории.
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
    await call.message.edit_text("🏪 Выберите нужный товар", reply_markup=markup)
    await state.set_state(ShopStates.viewing_goods)


# --- Пагинация товаров в категории
@router.callback_query(F.data.startswith('goods-page_'), ShopStates.viewing_goods)
async def navigate_goods(call: CallbackQuery):
    """
    Пагинация по списку товаров в выбранной категории.
    Формат: goods-page_{category}_{page}
    """
    prefix = "goods-page_"
    tail = call.data[len(prefix):]  # "{category_name}_{page}"
    category_name, current_index = tail.rsplit("_", 1)  # <-- rsplit защищает от '_' в категории
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
    await call.message.edit_text("🏪 Выберите нужный товар", reply_markup=markup)


# --- Карточка товара — БЕЗ состояния
@router.callback_query(F.data.startswith('item_'))
async def item_info_callback_handler(call: CallbackQuery):
    """
    Показывает подробную информацию о товаре.
    Работает всегда (без FSM), чтобы «Назад» из любых мест открывал карточку.
    """
    item_name = call.data[5:]
    item_info_list = get_item_info(item_name)
    if not item_info_list:
        await call.answer("Товар не найден", show_alert=True)
        return

    category = item_info_list['category_name']
    quantity = (
        'Количество - неограниченно'
        if check_value(item_name)
        else f'Количество - {select_item_values_amount(item_name)} шт.'
    )
    markup = item_info(item_name, category)
    await call.message.edit_text(
        f'🏪 Товар {item_name}\n'
        f'Описание: {item_info_list["description"]}\n'
        f'Цена - {item_info_list["price"]}₽\n'
        f'{quantity}',
        reply_markup=markup
    )


# --- Купленные товары пользователя (эта часть оставляем с FSM)
@router.callback_query(F.data == "bought_items")
async def bought_items_callback_handler(call: CallbackQuery):
    """
    Показывает список купленных пользователем товаров (со своей пагинацией).
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
    await call.message.edit_text("Купленные товары:", reply_markup=markup)


# --- Пагинация купленных товаров
@router.callback_query(F.data.startswith('bought-goods-page_'))
async def navigate_bought_items(call: CallbackQuery):
    """
    Пагинация по списку купленных товаров пользователя.
    Формат: 'bought-goods-page_{data}_{page}', где data = 'user' или user_id.
    """
    parts = call.data.split('_')
    if len(parts) < 3:
        await call.answer("Некорректные данные пагинации")
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
    await call.message.edit_text("Купленные товары:", reply_markup=markup)


# --- Информация о купленном товаре
@router.callback_query(F.data.startswith('bought-item:'))
async def bought_item_info_callback_handler(call: CallbackQuery):
    """
    Показывает детальную информацию о купленном товаре.
    """
    _, item_id, back_data = call.data.split(':', 2)
    item = get_bought_item_info(item_id)
    if not item:
        await call.answer("Покупка не найдена", show_alert=True)
        return

    await call.message.edit_text(
        f'<b>🧾 Товар</b>: <code>{item["item_name"]}</code>\n'
        f'<b>💵 Цена</b>: <code>{item["price"]}</code>₽\n'
        f'<b>🕒 Дата покупки</b>: <code>{item["bought_datetime"]}</code>\n'
        f'<b>🧾 Уникальный ID</b>: <code>{item["unique_id"]}</code>\n'
        f'<b>🔑 Значение</b>:\n<code>{item["value"]}</code>',
        parse_mode='HTML',
        reply_markup=back(back_data)
    )
