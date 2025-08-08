from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StatesGroup, State

from bot.database.models import Permission
from bot.database.methods import (
    check_item, delete_item, select_items, get_item_info,
    get_goods_info, delete_item_from_position
)
from bot.keyboards.inline import (
    back, paginated_keyboard, simple_buttons
)
from bot.logger_mesh import audit_logger
from bot.filters import HasPermissionFilter

router = Router()


class GoodsFSM(StatesGroup):
    """FSM для сценариев управления позициями."""
    waiting_item_name_delete = State()
    waiting_item_name_show = State()


# --- Главное меню управления позициями (SHOP_MANAGE)
@router.callback_query(F.data == 'goods_management', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def goods_management_callback_handler(call: CallbackQuery):
    """
    Открывает меню управления позициями (товарами).
    """
    actions = [
        ("➕ Добавить позицию", "add_item"),
        ("➕ Добавить товар в позицию", "update_item_amount"),
        ("📝 Изменить позицию", "update_item"),
        ("❌ Удалить позицию", "delete_item"),
        ("📄 Показать товары в позиции", "show__items_in_position"),
        ("⬅️ Назад", "console")
    ]
    markup = simple_buttons(actions, per_row=1)
    await call.message.edit_text('⛩️ Меню управления позициями', reply_markup=markup)


# --- Удаление позиции — запрашиваем название (SHOP_MANAGE)
@router.callback_query(F.data == 'delete_item', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def delete_item_callback_handler(call: CallbackQuery, state):
    """
    Запрашивает название позиции для удаления.
    """
    await call.message.edit_text('Введите название позиции', reply_markup=back("goods_management"))
    await state.set_state(GoodsFSM.waiting_item_name_delete)


# --- Обработка названия для удаления (SHOP_MANAGE)
@router.message(GoodsFSM.waiting_item_name_delete, F.text)
async def delete_str_item(message: Message, state):
    """
    Удаляет позицию по введённому названию.
    """
    item_name = message.text
    item = check_item(item_name)
    if not item:
        await message.answer(
            '❌ Позиция не удалена (Такой позиции не существует)',
            reply_markup=back('goods_management')
        )
    else:
        delete_item(item_name)
        await message.answer(
            '✅ Позиция удалена',
            reply_markup=back('goods_management')
        )
        admin_info = await message.bot.get_chat(message.from_user.id)
        audit_logger.info(
            f"Пользователь {message.from_user.id} ({admin_info.first_name}) удалил позицию \"{item_name}\""
        )
    await state.clear()


# --- Показ товаров в позиции (SHOP_MANAGE)
@router.callback_query(F.data == 'show__items_in_position', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def show_items_callback_handler(call: CallbackQuery, state):
    """
    Запрашивает название позиции для показа её товаров.
    """
    await call.message.edit_text('Введите название позиции', reply_markup=back("goods_management"))
    await state.set_state(GoodsFSM.waiting_item_name_show)


# --- Обработка названия позиции для показа товаров (SHOP_MANAGE)
@router.message(GoodsFSM.waiting_item_name_show, F.text)
async def show_str_item(message: Message, state):
    """
    Показывает все товары в выбранной позиции (с пагинацией).
    """
    item_name = message.text.strip()
    item = check_item(item_name)
    if not item:
        await message.answer(
            '❌ Товаров нет (Такой позиции не существует)',
            reply_markup=back('goods_management')
        )
        await state.clear()
        return

    goods = select_items(item_name)  # list[int]
    if not goods:
        await message.answer(
            'ℹ️ В этой позиции пока нет товаров.',
            reply_markup=back('goods_management')
        )
        await state.clear()
        return

    markup = paginated_keyboard(
        items=goods,
        item_text=lambda g: str(g),
        item_callback=lambda g: f"show-item_{g}_{item_name}_goods-in-item-page_{item_name}_0",
        page=0,
        per_page=10,
        back_cb="goods_management",
        nav_cb_prefix=f"goods-in-item-page_{item_name}_"
    )
    await message.answer('Товары в позиции:', reply_markup=markup)
    await state.clear()


# --- Пагинация товаров внутри позиции (SHOP_MANAGE)
@router.callback_query(F.data.startswith('goods-in-item-page_'), HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def navigate_items_in_goods(call: CallbackQuery):
    """
    Листает товары внутри позиции.
    Формат callback_data: goods-in-item-page_{item_name}_{page}
    """
    payload = call.data[len('goods-in-item-page_'):]
    try:
        item_name, page_str = payload.rsplit('_', 1)
        current_index = int(page_str)
    except ValueError:
        item_name, current_index = payload, 0

    goods = select_items(item_name)
    if not goods:
        await call.message.edit_text('ℹ️ В этой позиции пока нет товаров.', reply_markup=back('goods_management'))
        return

    per_page = 10
    max_page = max((len(goods) - 1) // per_page, 0)
    current_index = max(0, min(current_index, max_page))

    markup = paginated_keyboard(
        items=goods,
        item_text=lambda g: str(g),
        item_callback=lambda g: f"show-item_{g}_{item_name}_goods-in-item-page_{item_name}_{current_index}",
        page=current_index,
        per_page=per_page,
        back_cb="goods_management",
        nav_cb_prefix=f"goods-in-item-page_{item_name}_"
    )
    await call.message.edit_text('Товары в позиции:', reply_markup=markup)


# --- Информация о товаре (SHOP_MANAGE)
@router.callback_query(F.data.startswith('show-item_'), HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def item_info_callback_handler(call: CallbackQuery):
    """
    Показывает информацию о товаре (внутри позиции).
    Формат callback_data:
      show-item_{id}_{item_name}_goods-in-item-page_{item_name}_{page}
    """
    payload = call.data[len('show-item_'):]  # "{id}_{item_name}_goods-in-item-page_{item_name}_{page}"

    # 1) отделяем id от остального
    first_sep = payload.find('_')
    if first_sep == -1:
        await call.answer("Некорректные данные", show_alert=True)
        return
    item_id_str = payload[:first_sep]
    rest = payload[first_sep + 1:]

    # 2) пробуем извлечь back_data
    marker = 'goods-in-item-page_'
    back_data = 'goods_management'
    idx = rest.find(marker)
    if idx != -1:
        back_data = rest[idx:]

    # 3) грузим данные
    try:
        item_id = int(item_id_str)
    except ValueError:
        await call.answer("Некорректный ID товара", show_alert=True)
        return

    item_info = get_goods_info(item_id)
    if not item_info:
        await call.answer("Товар не найден", show_alert=True)
        return

    position_info = get_item_info(item_info["item_name"])

    actions = [
        ("❌ Удалить товар", f"delete-item-from-position_{item_id}_{back_data}"),
        ("⬅️ Назад", back_data),
    ]
    markup = simple_buttons(actions, per_row=1)

    await call.message.edit_text(
        f'<b>Позиция</b>: <code>{item_info["item_name"]}</code>\n'
        f'<b>Цена</b>: <code>{position_info["price"]}</code>₽\n'
        f'<b>Уникальный ID</b>: <code>{item_info["id"]}</code>\n'
        f'<b>Товар</b>:\n<code>{item_info["value"]}</code>',
        parse_mode='HTML',
        reply_markup=markup
    )


# --- Удаление товара из позиции (SHOP_MANAGE)
@router.callback_query(
    F.data.startswith('delete-item-from-position_'),
    HasPermissionFilter(permission=Permission.SHOP_MANAGE)
)
async def process_delete_item_from_position(call: CallbackQuery):
    """
    Формат callback_data: delete-item-from-position_{id}_{back_data}
    где back_data = goods-in-item-page_{item_name}_{page}
    """
    payload = call.data[len('delete-item-from-position_'):]  # "{id}_{back_data}"
    try:
        item_id_str, back_data = payload.split('_', 1)
        item_id = int(item_id_str)
    except ValueError:
        await call.answer("Некорректные данные", show_alert=True)
        return

    item_info = get_goods_info(item_id)
    if not item_info:
        await call.answer("Товар уже удалён или не найден", show_alert=True)
        await call.message.edit_text("Товары в позиции:", reply_markup=back(back_data))
        return

    position_name = item_info["item_name"]
    delete_item_from_position(item_id)

    # Перерисовываем страницу со списком, если надо
    if back_data.startswith("goods-in-item-page_"):
        try:
            _, rest = back_data.split("goods-in-item-page_", 1)
            item_name, page_str = rest.rsplit("_", 1)
            page = int(page_str)
        except Exception:
            await call.message.edit_text('✅ Товар удалён', reply_markup=back(back_data))
            return

        goods = select_items(item_name)
        if not goods:
            await call.message.edit_text('ℹ️ В этой позиции больше нет товаров.', reply_markup=back("goods_management"))
        else:
            per_page = 10
            max_page = max((len(goods) - 1) // per_page, 0)
            page = max(0, min(page, max_page))
            markup = paginated_keyboard(
                items=goods,
                item_text=lambda g: str(g),
                item_callback=lambda g: f"show-item_{g}_{item_name}_goods-in-item-page_{item_name}_{page}",
                page=page,
                per_page=per_page,
                back_cb="goods_management",
                nav_cb_prefix=f"goods-in-item-page_{item_name}_"
            )
            await call.message.edit_text('✅ Товар удалён\n\nТовары в позиции:', reply_markup=markup)
    else:
        await call.message.edit_text('✅ Товар удалён', reply_markup=back(back_data))

    admin_info = await call.message.bot.get_chat(call.from_user.id)
    audit_logger.info(
        f"Пользователь {call.from_user.id} ({admin_info.first_name}) удалил товар с id={item_id} из позиции {position_name or '<?>'}"
    )
