from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StatesGroup, State

from bot.database.models import Permission
from bot.database.methods import (
    check_item, add_values_to_item, update_item, check_value, delete_only_items
)
from bot.keyboards.inline import back, question_buttons, simple_buttons
from bot.logger_mesh import audit_logger
from bot.filters import HasPermissionFilter
from bot.misc import TgConfig

router = Router()


class UpdateItemFSM(StatesGroup):
    """
    FSM для сценариев обновления позиции:
    1) Добавление количества (values) к существующей позиции,
    2) Полное обновление позиции (имя, описание, цена, бесконечность/обычная, values).
    """
    # Добавление товаров к позиции
    waiting_item_name_for_amount_upd = State()
    waiting_item_values_upd = State()

    # Полное обновление позиции
    waiting_item_name_for_update = State()
    waiting_item_new_name = State()
    waiting_item_description = State()
    waiting_item_price = State()
    waiting_make_infinity = State()
    waiting_single_value = State()
    waiting_multiple_values = State()


# ==============================
#  БЛОК 1. Добавление товаров к позиции
# ==============================

@router.callback_query(F.data == 'update_item_amount', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def update_item_amount_callback_handler(call: CallbackQuery, state):
    """
    Запускает сценарий добавления товаров к существующей позиции.
    """
    await call.message.edit_text('Введите название позиции', reply_markup=back("goods_management"))
    await state.set_state(UpdateItemFSM.waiting_item_name_for_amount_upd)


@router.message(UpdateItemFSM.waiting_item_name_for_amount_upd, F.text)
async def check_item_name_for_amount_upd(message: Message, state):
    """
    Проверяем, что позиция существует и что она НЕ бесконечная.
    Если позиция бесконечная — values добавлять нельзя.
    """
    item_name = message.text.strip()
    item = check_item(item_name)
    if not item:
        await message.answer('❌ Товар не может быть добавлен (такой позиции не существует)',
                             reply_markup=back('goods_management'))
        return

    # Если позиция бесконечная, дополнять values логически нельзя
    if check_value(item_name):
        await message.answer('❌ Товар не может быть добавлен (у данной позиции бесконечный товар)',
                             reply_markup=back('goods_management'))
        return

    # Иначе начинаем копить values
    await state.update_data(item_name=item_name)
    await message.answer(
        'Введите товары для позиции по одному сообщению.\n'
        'Когда закончите ввод — нажмите «Добавить указанные товары».',
        reply_markup=back("goods_management")
    )
    await state.set_state(UpdateItemFSM.waiting_item_values_upd)


@router.message(UpdateItemFSM.waiting_item_values_upd, F.text)
async def updating_item_values(message: Message, state):
    """
    Накапливаем values для позиции (обычный режим).
    Кнопка “Завершить” показывается после первого значения.
    """
    data = await state.get_data()
    values = data.get('item_values', [])
    values.append(message.text)
    await state.update_data(item_values=values)

    await message.answer(
        f'✅ Товар «{message.text}» добавлен в список ({len(values)} шт.)',
        reply_markup=simple_buttons([
            ("Добавить указанные товары", "finish_updating_items"),
            ("⬅️ Назад", "goods_management")
        ], per_row=1)
    )


@router.callback_query(F.data == 'finish_updating_items', UpdateItemFSM.waiting_item_values_upd)
async def updating_item_amount(call: CallbackQuery, state):
    """
    Завершаем добавление новых товаров (values) к позиции.
    """
    data = await state.get_data()
    item_name = data.get('item_name')
    raw_values: list[str] = data.get("item_values", []) or []

    added = 0
    skipped_db_dup = 0
    skipped_batch_dup = 0
    skipped_invalid = 0
    seen_in_batch: set[str] = set()

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

    text_lines = [f"✅ Товары добавлены", f"📦 Добавлено товаров: <b>{added}</b>"]
    if skipped_db_dup:
        text_lines.append(f"↩️ Пропущено (уже были в БД): <b>{skipped_db_dup}</b>")
    if skipped_batch_dup:
        text_lines.append(f"🔁 Пропущено (дубль в вводе): <b>{skipped_batch_dup}</b>")
    if skipped_invalid:
        text_lines.append(f"🚫 Пропущено (пустые/некорректные): <b>{skipped_invalid}</b>")

    await call.message.edit_text("\n".join(text_lines), parse_mode="HTML", reply_markup=back('goods_management'))

    # Опционально: уведомление в группу/канал, если настроено
    group_id = TgConfig.GROUP_ID if getattr(TgConfig, "GROUP_ID", None) not in (None, -988765433) else None
    if group_id:
        try:
            await call.message.bot.send_message(
                chat_id=group_id,
                text=(f'🎁 Залив\n'
                      f'🏷️ Товар: <b>{item_name}</b>\n'
                      f'📦 Количество: <b>{added}</b>'),
                parse_mode='HTML'
            )
        except Exception:
            # Не мешаем сценарию, если отправка не удалась
            pass

    admin_info = await call.message.bot.get_chat(call.from_user.id)
    audit_logger.info(
        f'Админ {call.from_user.id} ({admin_info.first_name}) добавил к позиции "{item_name}" {added} шт.')
    await state.clear()


# ==============================
#  БЛОК 2. Полное обновление позиции
# ==============================

@router.callback_query(F.data == 'update_item', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def update_item_callback_handler(call: CallbackQuery, state):
    """
    Запускает сценарий полного обновления позиции.
    """
    await call.message.edit_text('Введите название позиции', reply_markup=back("goods_management"))
    await state.set_state(UpdateItemFSM.waiting_item_name_for_update)


@router.message(UpdateItemFSM.waiting_item_name_for_update, F.text)
async def check_item_name_for_update(message: Message, state):
    """
    Проверка существования позиции. Если есть — запрашиваем новое имя.
    """
    item_name = message.text.strip()
    item = check_item(item_name)
    if not item:
        await message.answer('❌ Позиция не может быть изменена (такой позиции не существует)',
                             reply_markup=back('goods_management'))
        return

    await state.update_data(item_old_name=item_name, item_category=item['category_name'])
    await message.answer('Введите новое имя для позиции:', reply_markup=back('goods_management'))
    await state.set_state(UpdateItemFSM.waiting_item_new_name)


@router.message(UpdateItemFSM.waiting_item_new_name, F.text)
async def update_item_name(message: Message, state):
    """
    Запрашиваем новое описание позиции.
    """
    await state.update_data(item_new_name=message.text.strip())
    await message.answer('Введите описание для позиции:', reply_markup=back('goods_management'))
    await state.set_state(UpdateItemFSM.waiting_item_description)


@router.message(UpdateItemFSM.waiting_item_description, F.text)
async def update_item_description(message: Message, state):
    """
    Запрашиваем новую цену позиции.
    """
    await state.update_data(item_description=message.text.strip())
    await message.answer('Введите цену для позиции (число в ₽):', reply_markup=back('goods_management'))
    await state.set_state(UpdateItemFSM.waiting_item_price)


@router.message(UpdateItemFSM.waiting_item_price, F.text)
async def update_item_price(message: Message, state):
    """
    Валидируем цену. Затем спрашиваем про режим “бесконечность”.
    """
    price_text = message.text.strip()
    if not price_text.isdigit():
        await message.answer('⚠️ Некорректное значение цены. Введите число.', reply_markup=back('goods_management'))
        return

    await state.update_data(item_price=int(price_text))
    data = await state.get_data()
    item_old_name = data.get('item_old_name')

    # Если позиция сейчас НЕ бесконечная — спросим, сделать ли её бесконечной
    if not check_value(item_old_name):
        await message.answer(
            'Вы хотите сделать товары бесконечными?',
            reply_markup=question_buttons('change_make_infinity', 'goods_management')
        )
    else:
        # иначе — спросим, отменить ли бесконечность
        await message.answer(
            'Вы хотите отменить бесконечные товары?',
            reply_markup=question_buttons('change_deny_infinity', 'goods_management')
        )
    await state.set_state(UpdateItemFSM.waiting_make_infinity)


@router.callback_query(F.data.startswith('change_'), UpdateItemFSM.waiting_make_infinity)
async def update_item_process(call: CallbackQuery, state):
    """
    Обрабатываем решение по бесконечности:
    - change_*_no   -> просто обновляем позицию без изменения values,
    - change_make_* -> ждём ОДНО значение и переводим позицию в бесконечную,
    - change_deny_* -> ждём список значений и переводим позицию в обычную.
    """
    parts = call.data.split('_')
    # Ожидаемые варианты: change_make_infinity_yes/no, change_deny_infinity_yes/no
    decision_scope = parts[1]  # make / deny
    decision_yesno = parts[3]  # yes / no

    data = await state.get_data()
    item_old_name = data.get('item_old_name')
    item_new_name = data.get('item_new_name')
    item_description = data.get('item_description')
    category = data.get('item_category')
    price = data.get('item_price')

    if decision_yesno == 'no':
        # Не меняем тип (остатки/бесконечность), просто апдейтим мета-данные
        update_item(item_old_name, item_new_name, item_description, price, category)
        await call.message.edit_text('✅ Позиция обновлена', reply_markup=back('goods_management'))
        admin_info = await call.message.bot.get_chat(call.from_user.id)
        audit_logger.info(
            f'Админ {call.from_user.id} ({admin_info.first_name}) обновил позицию "{item_old_name}" → "{item_new_name}"')
        await state.clear()
        return

    # decision_yesno == 'yes'
    if decision_scope == 'make':
        # Переводим в бесконечный режим: ждём ОДНО значение
        await call.message.edit_text('Введите одно значение товара для позиции:', reply_markup=back('goods_management'))
        await state.set_state(UpdateItemFSM.waiting_single_value)
    else:
        # Переводим в обычный режим: собираем МНОЖЕСТВО values
        await call.message.edit_text(
            'Введите товары для позиции по одному сообщению.\n'
            'Когда закончите ввод — нажмите «Добавить указанные товары».',
            reply_markup=back("goods_management")
        )
        await state.set_state(UpdateItemFSM.waiting_multiple_values)


@router.message(UpdateItemFSM.waiting_single_value, F.text)
async def update_item_infinity(message: Message, state):
    """
    Перевод в бесконечный режим:
    - очищаем текущие values,
    - добавляем единичное значение is_infinity=True,
    - обновляем мета-данные позиции.
    """
    data = await state.get_data()
    item_old_name = data.get('item_old_name')
    item_new_name = data.get('item_new_name')
    item_description = data.get('item_description')
    category = data.get('item_category')
    price = data.get('item_price')
    value = message.text

    # Чистим values и записываем "бесконечное" значение
    delete_only_items(item_old_name)
    add_values_to_item(item_old_name, value, True)
    update_item(item_old_name, item_new_name, item_description, price, category)

    await message.answer('✅ Позиция обновлена', reply_markup=back('goods_management'))
    admin_info = await message.bot.get_chat(message.from_user.id)
    audit_logger.info(
        f'Админ {message.from_user.id} ({admin_info.first_name}) обновил позицию "{item_old_name}" → "{item_new_name}"')
    await state.clear()


@router.message(UpdateItemFSM.waiting_multiple_values, F.text)
async def updating_item(message: Message, state):
    """
    Перевод в обычный (не бесконечный) режим:
    - накапливаем значения,
    - затем кнопкой “Завершить” применим изменения.
    """
    data = await state.get_data()
    values = data.get('item_values', [])
    values.append(message.text)
    await state.update_data(item_values=values)

    await message.answer(
        f'✅ Товар «{message.text}» добавлен в список ({len(values)} шт.)',
        reply_markup=simple_buttons([
            ("Добавить указанные товары", "finish_update_item"),
            ("⬅️ Назад", "goods_management")
        ], per_row=1)
    )


@router.callback_query(F.data == 'finish_update_item', UpdateItemFSM.waiting_multiple_values)
async def update_item_no_infinity(call: CallbackQuery, state):
    """
    Финал перевода в обычный режим:
    - очищаем текущие values,
    - добавляем все накопленные значения is_infinity=False,
    - обновляем мета-данные позиции.
    """
    data = await state.get_data()
    item_old_name = data.get('item_old_name')
    item_new_name = data.get('item_new_name')
    item_description = data.get('item_description')
    category = data.get('item_category')
    price = data.get('item_price')
    raw_values: list[str] = data.get("item_values", []) or []

    added = 0
    skipped_db_dup = 0
    skipped_batch_dup = 0
    skipped_invalid = 0
    seen_in_batch: set[str] = set()

    delete_only_items(item_old_name)

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
        if add_values_to_item(item_old_name, v_norm, False):
            added += 1
        else:
            skipped_db_dup += 1

    text_lines = [f"✅ Позиция обновлена", f"📦 Добавлено товаров: <b>{added}</b>"]
    if skipped_db_dup:
        text_lines.append(f"↩️ Пропущено (уже были в БД): <b>{skipped_db_dup}</b>")
    if skipped_batch_dup:
        text_lines.append(f"🔁 Пропущено (дубль в вводе): <b>{skipped_batch_dup}</b>")
    if skipped_invalid:
        text_lines.append(f"🚫 Пропущено (пустые/некорректные): <b>{skipped_invalid}</b>")

    update_item(item_old_name, item_new_name, item_description, price, category)

    # Опционально: уведомление в группу/канал, если настроено
    group_id = TgConfig.GROUP_ID if getattr(TgConfig, "GROUP_ID", None) not in (None, -988765433) else None
    if group_id:
        try:
            await call.message.bot.send_message(
                chat_id=group_id,
                text=(f'🎁 Залив\n'
                      f'🏷️ Товар: <b>{item_new_name}</b>\n'
                      f'📦 Количество: <b>{added}</b>'),
                parse_mode='HTML'
            )
        except Exception:
            # Не мешаем сценарию, если отправка не удалась
            pass

    await call.message.edit_text("\n".join(text_lines), parse_mode="HTML", reply_markup=back('goods_management'))
    admin_info = await call.message.bot.get_chat(call.from_user.id)
    audit_logger.info(
        f'Админ {call.from_user.id} ({admin_info.first_name}) обновил позицию "{item_old_name}" → "{item_new_name}"')
    await state.clear()
