from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StatesGroup, State

from bot.database.models import Permission
from bot.database.methods import (
    check_category, check_item, create_item, add_values_to_item
)
from bot.keyboards.inline import back, question_buttons, simple_buttons
from bot.logger_mesh import audit_logger
from bot.filters import HasPermissionFilter
from bot.misc import TgConfig

router = Router()


class AddItemFSM(StatesGroup):
    """
    FSM для пошагового создания позиции (товара):
    1) имя,
    2) описание,
    3) цена,
    4) категория,
    5) режим (бесконечный или нет),
    6) ввод значений товара (одно / много).
    """
    waiting_item_name = State()
    waiting_item_description = State()
    waiting_item_price = State()
    waiting_category = State()
    waiting_infinity = State()
    waiting_values = State()
    waiting_single_value = State()


# --- Старт сценария создания позиции (требуются права SHOP_MANAGE)
@router.callback_query(F.data == 'add_item', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def add_item_callback_handler(call: CallbackQuery, state):
    """
    Запрашиваем у администратора имя новой позиции.
    """
    await call.message.edit_text('Введите название позиции', reply_markup=back("goods_management"))
    await state.set_state(AddItemFSM.waiting_item_name)


# --- Проверка имени позиции (не должно существовать)
@router.message(AddItemFSM.waiting_item_name, F.text)
async def check_item_name_for_add(message: Message, state):
    """
    Если позиция уже существует — сообщаем; иначе сохраняем имя и просим описание.
    """
    item_name = message.text.strip()
    item = check_item(item_name)
    if item:
        await message.answer(
            '❌ Позиция не может быть создана (такая позиция уже существует)',
            reply_markup=back('goods_management')
        )
        return

    await state.update_data(item_name=item_name)
    await message.answer('Введите описание для позиции:', reply_markup=back('goods_management'))
    await state.set_state(AddItemFSM.waiting_item_description)


# --- Ввод описания
@router.message(AddItemFSM.waiting_item_description, F.text)
async def add_item_description(message: Message, state):
    """
    Сохраняем описание и переходим к цене.
    """
    await state.update_data(item_description=message.text.strip())
    await message.answer('Введите цену для позиции (число в ₽):', reply_markup=back('goods_management'))
    await state.set_state(AddItemFSM.waiting_item_price)


# --- Ввод цены
@router.message(AddItemFSM.waiting_item_price, F.text)
async def add_item_price(message: Message, state):
    """
    Валидируем цену и спрашиваем категорию.
    """
    price_text = message.text.strip()
    if not price_text.isdigit():
        await message.answer('⚠️ Некорректное значение цены. Введите число.', reply_markup=back('goods_management'))
        return

    await state.update_data(item_price=int(price_text))
    await message.answer('Введите категорию, к которой будет относиться позиция:',
                         reply_markup=back('goods_management'))
    await state.set_state(AddItemFSM.waiting_category)


# --- Проверка категории
@router.message(AddItemFSM.waiting_category, F.text)
async def check_category_for_add_item(message: Message, state):
    """
    Категория должна существовать; затем спрашиваем про бесконечность товара.
    """
    category_name = message.text.strip()
    category = check_category(category_name)
    if not category:
        await message.answer(
            '❌ Позиция не может быть создана (категория для привязки введена неверно)',
            reply_markup=back('goods_management')
        )
        return

    await state.update_data(item_category=category_name)
    await message.answer(
        'У этой позиции будут бесконечные товары? (всем будет высылаться одна копия значения)',
        reply_markup=question_buttons('infinity', 'goods_management')
    )
    await state.set_state(AddItemFSM.waiting_infinity)


# --- Выбор режима: бесконечные товары / конечные
@router.callback_query(F.data.startswith('infinity_'), AddItemFSM.waiting_infinity)
async def adding_value_to_position(call: CallbackQuery, state):
    """
    Если бесконечно — ждём одно значение.
    Если нет — собираем множество значений до завершения.
    """
    answer = call.data.split('_')[1]
    await state.update_data(is_infinity=(answer == 'yes'))

    if answer == 'no':
        # Кнопка “Завершить добавление” появится после первого значения
        await call.message.edit_text(
            'Введите товары для позиции по одному сообщению.\n'
            'Когда закончите ввод — нажмите «Добавить указанные товары».',
            reply_markup=back("goods_management")
        )
        await state.set_state(AddItemFSM.waiting_values)
    else:
        await call.message.edit_text(
            'Введите одно значение товара для позиции:',
            reply_markup=back('goods_management')
        )
        await state.set_state(AddItemFSM.waiting_single_value)


# --- Сбор значений (НЕ бесконечный режим)
@router.message(AddItemFSM.waiting_values, F.text)
async def collect_item_value(message: Message, state):
    """
    Копим значения в FSM-состоянии. После первого — даём кнопку “Завершить”.
    """
    data = await state.get_data()
    values = data.get('item_values', [])
    values.append(message.text)
    await state.update_data(item_values=values)

    # Показываем прогресс и кнопку “Завершить добавление”
    await message.answer(
        f'✅ Товар «{message.text}» добавлен в список ({len(values)} шт.)',
        reply_markup=simple_buttons([
            ("Добавить указанные товары", "finish_adding_items"),
            ("⬅️ Назад", "goods_management")
        ], per_row=1)
    )


# --- Завершить добавление всех значений (НЕ бесконечный режим)
@router.callback_query(F.data == 'finish_adding_items', AddItemFSM.waiting_values)
async def finish_adding_items_callback_handler(call: CallbackQuery, state):
    """
    Создаём позицию, добавляем все собранные значения, уведомляем группу (если задана).
    """
    data = await state.get_data()
    item_name = data.get('item_name')
    item_description = data.get('item_description')
    item_price = data.get('item_price')
    category_name = data.get('item_category')
    raw_values: list[str] = data.get("item_values", []) or []

    added = 0
    skipped_db_dup = 0
    skipped_batch_dup = 0
    skipped_invalid = 0
    seen_in_batch: set[str] = set()

    # создаём позицию
    create_item(item_name, item_description, item_price, category_name)

    for v in raw_values:
        v_norm = (v or "").strip()
        if not v_norm:
            skipped_invalid += 1
            continue

        # Дубликат внутри текущей пачки
        if v_norm in seen_in_batch:
            skipped_batch_dup += 1
            continue
        seen_in_batch.add(v_norm)

        # Пытаемся вставить — False означает, что такое уже есть в БД
        if add_values_to_item(item_name, v_norm, False):
            added += 1
        else:
            skipped_db_dup += 1

    text_lines = [f"✅ Позиция создана.", f"📦 Добавлено товаров: <b>{added}</b>"]
    if skipped_db_dup:
        text_lines.append(f"↩️ Пропущено (уже были в БД): <b>{skipped_db_dup}</b>")
    if skipped_batch_dup:
        text_lines.append(f"🔁 Пропущено (дубль в вводе): <b>{skipped_batch_dup}</b>")
    if skipped_invalid:
        text_lines.append(f"🚫 Пропущено (пустые/некорректные): <b>{skipped_invalid}</b>")

    await call.message.edit_text("\n".join(text_lines), parse_mode="HTML", reply_markup=back("goods_management"))

    # опционально уведомляем группу
    group_id = TgConfig.GROUP_ID if TgConfig.GROUP_ID != -988765433 else None
    if group_id:
        try:
            await call.message.bot.send_message(
                chat_id=group_id,
                text=(
                    f'🎁 Залив\n'
                    f'🏷️ Товар: <b>{item_name}</b>\n'
                    f'📦 Количество: <b>{added}</b>'
                ),
                parse_mode='HTML'
            )
        except Exception:
            pass

    admin_info = await call.message.bot.get_chat(call.from_user.id)
    audit_logger.info(
        f"Пользователь {call.from_user.id} ({admin_info.first_name}) создал новую позицию \"{item_name}\"")
    await state.clear()


# --- Ввод одного значения (Бесконечный режим)
@router.message(AddItemFSM.waiting_single_value, F.text)
async def finish_adding_item_callback_handler(message: Message, state):
    """
    Создаём позицию и добавляем одно “бесконечное” значение. Уведомляем группу (если задана).
    """
    data = await state.get_data()
    item_name = data.get('item_name')
    item_description = data.get('item_description')
    item_price = data.get('item_price')
    category_name = data.get('item_category')

    single_value = message.text.strip()
    if not single_value:
        await message.answer('⚠️ Значение не может быть пустым.', reply_markup=back('goods_management'))
        return

    # 1) создаём позицию
    create_item(item_name, item_description, item_price, category_name)
    # 2) добавляем 1 «бесконечное» значение
    add_values_to_item(item_name, single_value, True)

    # 3) опционально уведомляем группу
    group_id = TgConfig.GROUP_ID if TgConfig.GROUP_ID != -988765433 else None
    if group_id:
        try:
            await message.bot.send_message(
                chat_id=group_id,
                text=(
                    f'🎁 Залив\n'
                    f'🏷️ Товар: <b>{item_name}</b>\n'
                    f'📦 Количество: <b>∞</b>'
                ),
                parse_mode='HTML'
            )
        except Exception:
            pass

    await message.answer('✅ Позиция создана, значение добавлено', reply_markup=back('goods_management'))
    admin_info = await message.bot.get_chat(message.from_user.id)
    audit_logger.info(
        f'Пользователь {message.from_user.id} ({admin_info.first_name}) '
        f'создал бесконечную позицию "{item_name}"'
    )
    await state.clear()
