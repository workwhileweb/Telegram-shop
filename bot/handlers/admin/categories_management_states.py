from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StatesGroup, State

from bot.database.models import Permission
from bot.database.methods import (
    check_category, create_category, delete_category, update_category
)
from bot.keyboards.inline import back, simple_buttons
from bot.filters import HasPermissionFilter
from bot.logger_mesh import audit_logger

router = Router()


class CategoryFSM(StatesGroup):
    """
    FSM-состояния для работы с категориями:
    - добавление,
    - удаление,
    - переименование.
    """
    waiting_add_category = State()
    waiting_delete_category = State()
    waiting_update_category = State()
    waiting_update_category_name = State()


# --- Главное меню управления категориями (SHOP_MANAGE)
@router.callback_query(F.data == 'categories_management', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def categories_callback_handler(call: CallbackQuery):
    """
    Открывает подменю управления категориями.
    """
    actions = [
        ("➕ Добавить категорию", "add_category"),
        ("✏️ Переименовать категорию", "update_category"),
        ("🗑 Удалить категорию", "delete_category"),
        ("⬅️ Назад", "console"),
    ]
    await call.message.edit_text(
        "⛩️ Меню управления категориями",
        reply_markup=simple_buttons(actions, per_row=1)
    )


# --- Начало добавления категории
@router.callback_query(F.data == 'add_category', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def add_category_callback_handler(call: CallbackQuery, state):
    """
    Запрашивает у администратора название новой категории.
    """
    await call.message.edit_text(
        "Введите название новой категории:",
        reply_markup=back("categories_management"),
    )
    await state.set_state(CategoryFSM.waiting_add_category)


# --- Обработка ввода названия новой категории
@router.message(CategoryFSM.waiting_add_category, F.text)
async def process_category_for_add(message: Message, state):
    """
    Создаёт новую категорию, если её ещё нет.
    """
    category_name = message.text.strip()

    if check_category(category_name):
        await message.answer(
            "❌ Категория не создана (такая уже существует)",
            reply_markup=back("categories_management"),
        )
    else:
        create_category(category_name)
        await message.answer(
            "✅ Категория создана",
            reply_markup=back("categories_management"),
        )
        admin_info = await message.bot.get_chat(message.from_user.id)
        audit_logger.info(
            f'Admin {message.from_user.id} ({admin_info.first_name}) created category "{category_name}"'
        )

    await state.clear()


# --- Начало удаления категории
@router.callback_query(F.data == 'delete_category', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def delete_category_callback_handler(call: CallbackQuery, state):
    """
    Запрашивает у администратора название категории для удаления.
    """
    await call.message.edit_text(
        "Введите название категории для удаления:",
        reply_markup=back("categories_management")
    )
    await state.set_state(CategoryFSM.waiting_delete_category)


# --- Обработка удаления категории
@router.message(CategoryFSM.waiting_delete_category, F.text)
async def process_category_for_delete(message: Message, state):
    """
    Удаляет категорию по имени, если она существует.
    """
    category_name = message.text.strip()

    if not check_category(category_name):
        await message.answer(
            "❌ Категория не удалена (такой категории не существует)",
            reply_markup=back("categories_management"),
        )
    else:
        # БД стоит FK на goods.category_name -> categories.name.
        # Если есть связанные позиции, удаление может быть запрещено (RESTRICT).
        delete_category(category_name)
        await message.answer(
            "✅ Категория удалена",
            reply_markup=back("categories_management")
        )
        admin_info = await message.bot.get_chat(message.from_user.id)
        audit_logger.info(
            f'Admin {message.from_user.id} ({admin_info.first_name}) deleted category "{category_name}"'
        )

    await state.clear()


# --- Начало переименования категории
@router.callback_query(F.data == 'update_category', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def update_category_callback_handler(call: CallbackQuery, state):
    """
    Запрашивает текущее имя категории для её переименования.
    """
    await call.message.edit_text(
        "Введите текущее название категории, которую нужно переименовать:",
        reply_markup=back("categories_management")
    )
    await state.set_state(CategoryFSM.waiting_update_category)


# --- Проверяем существование категории, затем просим новое имя
@router.message(CategoryFSM.waiting_update_category, F.text)
async def check_category_for_update(message: Message, state):
    """
    Проверяет, что категория существует, затем просит указать новое имя.
    """
    old_name = message.text.strip()

    # Сначала убеждаемся, что такая категория есть
    if not check_category(old_name):
        await message.answer(
            "❌ Категория не может быть обновлена (такой категории не существует)",
            reply_markup=back("categories_management")
        )
        await state.clear()
        return

    await state.update_data(old_category=old_name)
    await message.answer(
        "Введите новое имя для категории:",
        reply_markup=back("categories_management")
    )
    await state.set_state(CategoryFSM.waiting_update_category_name)


# --- Завершаем обновление категории
@router.message(CategoryFSM.waiting_update_category_name, F.text)
async def check_category_name_for_update(message: Message, state):
    """
    Переименовывает категорию в новое название.
    """
    new_name = message.text.strip()
    data = await state.get_data()
    old_name = data.get("old_category")

    # Если новая категория уже есть — отказываем.
    if check_category(new_name):
        await message.answer(
            "❌ Переименование невозможно (категория с таким именем уже существует)",
            reply_markup=back("categories_management"),
        )
        await state.clear()
        return

    # Переименовываем (метод update_category должен обработать перенос ссылок из goods)
    update_category(old_name, new_name)
    await message.answer(
        f'✅ Категория "{old_name}" переименована в "{new_name}"',
        reply_markup=back("categories_management"),
    )

    admin_info = await message.bot.get_chat(message.from_user.id)
    audit_logger.info(
        f'Admin {message.from_user.id} ({admin_info.first_name}) renamed category "{old_name}" to "{new_name}"'
    )

    await state.clear()
