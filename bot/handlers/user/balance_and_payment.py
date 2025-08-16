import json
import datetime
from decimal import Decimal, ROUND_HALF_UP

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, SuccessfulPayment
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State

from bot.database.methods import (
    get_user_balance, get_item_info, get_item_value, buy_item, add_bought_item,
    buy_item_for_balance, start_operation, select_unfinished_operations,
    get_user_referral, finish_operation, update_balance, create_operation
)
from bot.keyboards import back, payment_menu, close, get_payment_choice
from bot.logger_mesh import audit_logger
from bot.misc import TgConfig, EnvKeys
from bot.handlers.other import _any_payment_method_enabled
from bot.misc.payment import quick_pay, check_payment_status, CryptoPayAPI, send_stars_invoice, STARS_PER_RUB
from bot.filters import ValidAmountFilter

router = Router()


class BalanceStates(StatesGroup):
    """
    Состояния FSM для сценария пополнения баланса.
    """
    waiting_amount = State()
    waiting_payment = State()


# --- Хэндлер: начало пополнения баланса
@router.callback_query(F.data == "replenish_balance")
async def replenish_balance_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя сумму для пополнения баланса.
    Разрешает вход, если доступен хотя бы один метод оплаты.
    """
    if not _any_payment_method_enabled():
        await call.answer('❌ Пополнение не настроено', show_alert=True)
        return

    await call.message.edit_text(
        '💰 Введите сумму для пополнения:',
        reply_markup=back('profile')
    )
    await state.set_state(BalanceStates.waiting_amount)


# --- Хэндлер: ввод суммы пополнения (валидная сумма)
@router.message(BalanceStates.waiting_amount, ValidAmountFilter())
async def replenish_balance_amount(message: Message, state: FSMContext):
    """
    Получает сумму и предлагает выбрать способ оплаты.
    """
    amount = int(message.text)
    await state.update_data(amount=amount)

    await message.answer(
        '💳 Выберите способ оплаты',
        reply_markup=get_payment_choice()
    )
    await state.set_state(BalanceStates.waiting_payment)


# --- Хэндлер: ввод суммы пополнения (некорректная сумма)
@router.message(BalanceStates.waiting_amount)
async def invalid_amount(message: Message, state: FSMContext):
    """
    Сообщает об ошибке, если сумма пополнения некорректна.
    """
    await message.answer(
        "❌ Неверная сумма пополнения. "
        "Сумма пополнения должна быть числом не меньше 20₽ и не более 10 000₽",
        reply_markup=back('replenish_balance')
    )


# --- Хэндлер: выбор способа оплаты
@router.callback_query(BalanceStates.waiting_payment, F.data.in_(['pay_yoomoney', 'pay_cryptopay', "pay_stars"]))
async def process_replenish_balance(call: CallbackQuery, state: FSMContext):
    """
    Создаёт платёж для выбранного способа и предлагает пользователю оплатить.
    Для Telegram Stars отправляем инвойс через Telegram Payments (currency='XTR'),
    дальше срабатывают общие pre_checkout и successful_payment хэндлеры.
    """
    data = await state.get_data()
    amount = data.get('amount')
    if amount is None:
        await call.answer("Сессия оплаты устарела. Начните заново.", show_alert=True)
        await call.message.edit_text("⛩️ Основное меню", reply_markup=back('back_to_menu'))
        await state.clear()
        return

    amount_dec = Decimal(amount).quantize(Decimal("1."), rounding=ROUND_HALF_UP)
    ttl_seconds = int(TgConfig.PAYMENT_TIME)

    if call.data == "pay_cryptopay":
        # Crypto Bot
        if not EnvKeys.CRYPTO_PAY_TOKEN:
            await call.answer("❌ CryptoPay не настроен", show_alert=True)
            return
        try:
            crypto = CryptoPayAPI()
            invoice = await crypto.create_invoice(
                amount=float(amount_dec),
                currency="RUB",
                accepted_assets="TON,USDT,BTC,ETH",
                payload=str(call.from_user.id),
                expires_in=TgConfig.PAYMENT_TIME
            )
        except Exception as e:
            await call.answer(f"❌ Ошибка при создании счёта: {e}", show_alert=True)
            return

        pay_url = invoice.get("mini_app_invoice_url")
        invoice_id = invoice.get("invoice_id")

        await state.update_data(invoice_id=invoice_id, payment_type="cryptopay")
        start_operation(call.from_user.id, int(amount_dec), invoice_id)

        await call.message.edit_text(
            f"💵 Сумма пополнения: {int(amount_dec)}₽.\n"
            f"⌛️ У вас есть {int(ttl_seconds / 60)} минут на оплату.\n"
            f"<b>❗️ После оплаты нажмите кнопку «Проверить оплату»</b>",
            reply_markup=payment_menu(pay_url)
        )

    elif call.data == "pay_yoomoney":
        # YooMoney
        if not (EnvKeys.ACCOUNT_NUMBER and EnvKeys.ACCESS_TOKEN):
            await call.answer("❌ YooMoney не настроен", show_alert=True)
            return
        try:
            label, url = quick_pay(int(amount_dec), call.from_user.id)
        except Exception as e:
            await call.answer(f"❌ Ошибка при создании счёта: {e}", show_alert=True)
            return

        start_operation(call.from_user.id, int(amount_dec), label)
        await state.update_data(label=label, payment_type="yoomoney")

        await call.message.edit_text(
            f'💵 Сумма пополнения: {int(amount_dec)}₽.\n'
            f'⌛️ У вас есть {int(ttl_seconds / 60)} минут на оплату.\n'
            f'<b>❗️ После оплаты нажмите кнопку «Проверить оплату»</b>',
            reply_markup=payment_menu(url)
        )

    elif call.data == "pay_stars":
        # Telegram Stars (XTR)
        try:
            await send_stars_invoice(
                bot=call.message.bot,
                chat_id=call.from_user.id,
                amount_rub=int(amount_dec),
            )
        except Exception as e:
            await call.answer(f"❌ Не удалось выставить счёт в Stars: {e}", show_alert=True)
            return

        await state.clear()


# --- Хэндлер: проверка оплаты (для методов, требующих ручной проверки)
@router.callback_query(F.data == "check")
async def checking_payment(call: CallbackQuery, state: FSMContext):
    """
    Проверка статуса оплаты и зачисление средств.
    Используется для CryptoPay/YooMoney.
    Для Telegram Stars НЕ используется (там автосообщение SuccessfulPayment).
    """
    user_id = call.from_user.id
    data = await state.get_data()
    payment_type = data.get("payment_type")

    if not payment_type:
        await call.answer("❌ Активных счетов не найдено. Начните пополнение заново.", show_alert=True)
        return

    # --- CryptoPay
    if payment_type == "cryptopay":
        invoice_id = data.get("invoice_id")
        if not invoice_id:
            await call.answer("❌ Счёт не найден. Начните заново.", show_alert=True)
            await state.clear()
            return

        try:
            crypto = CryptoPayAPI()
            info = await crypto.get_invoice(invoice_id)
        except Exception as e:
            await call.answer(f"❌ Ошибка проверки: {e}", show_alert=True)
            return

        status = info.get("status")
        if status == "paid":
            balance_amount = int(Decimal(str(info.get("amount", "0"))).quantize(Decimal("1.")))
            referral_id = get_user_referral(user_id)

            finish_operation(invoice_id)

            if referral_id and TgConfig.REFERRAL_PERCENT:
                try:
                    referral_operation = int(
                        Decimal(TgConfig.REFERRAL_PERCENT) / Decimal(100) * Decimal(balance_amount))
                    update_balance(referral_id, referral_operation)
                    await call.bot.send_message(
                        referral_id,
                        f'✅ Вы получили {referral_operation}₽ от вашего реферала {call.from_user.first_name}',
                        reply_markup=close()
                    )
                except Exception:
                    pass

            create_operation(user_id, balance_amount, datetime.datetime.now())
            update_balance(user_id, balance_amount)

            await call.message.edit_text(
                f'✅ Баланс пополнен на {balance_amount}₽',
                reply_markup=back('profile')
            )
            await state.clear()

        elif status == "active":
            await call.answer("⌛️ Платёж ещё не оплачен.")
        else:
            await call.answer("❌ Срок действия счёта истёк.", show_alert=True)

    # --- YooMoney
    elif payment_type == "yoomoney":
        label = data.get("label")
        if not label:
            await call.answer("❌ Счёт не найден. Начните заново.", show_alert=True)
            await state.clear()
            return

        info = select_unfinished_operations(label)
        if not info:
            await call.answer('❌ Счёт не найден', show_alert=True)
            return

        operation_value = int(info[0])
        try:
            payment_status = await check_payment_status(label)
        except Exception as e:
            await call.answer(f"❌ Ошибка проверки: {e}", show_alert=True)
            return

        if payment_status == "success":
            referral_id = get_user_referral(user_id)
            finish_operation(label)

            if referral_id and TgConfig.REFERRAL_PERCENT:
                try:
                    referral_operation = int(
                        Decimal(TgConfig.REFERRAL_PERCENT) / Decimal(100) * Decimal(operation_value))
                    update_balance(referral_id, referral_operation)
                    await call.bot.send_message(
                        referral_id,
                        f'✅ Вы получили {referral_operation}₽ от вашего реферала {call.from_user.first_name}',
                        reply_markup=close()
                    )
                except Exception:
                    pass

            create_operation(user_id, operation_value, datetime.datetime.now())
            update_balance(user_id, operation_value)

            await call.message.edit_text(
                f'✅ Баланс пополнен на {operation_value}₽',
                reply_markup=back('profile')
            )
            await state.clear()
        else:
            await call.answer('⌛️ Платёж ещё не оплачен.')


# --- Хэндлер: Telegram Payments pre-checkout (Stars обязательны)
@router.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery):
    """
    Telegram требует обязательно ответить ok=True перед оплатой.
    """
    await query.answer(ok=True)


# --- Хэндлер: успешная оплата через Telegram Payments (в т.ч. Stars)
@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """
    Обработка успешной оплаты Telegram Payments.
    - XTR: total_amount = кол-во ⭐. Рубли берем из payload (предпочтительно),
      либо пересчитываем stars -> rub по STARS_PER_RUB.
    """
    sp: SuccessfulPayment = message.successful_payment
    user_id = message.from_user.id

    if sp.currency != "XTR":
        # Для будущих провайдеров через Telegram Payments
        return

    payload = {}
    try:
        if sp.invoice_payload:
            payload = json.loads(sp.invoice_payload)
    except Exception:
        payload = {}

    stars = int(sp.total_amount)
    # Если мы клали сумму в рублях в payload — используем её (во избежание расхождений по курсу/округлению)
    if "amount_rub" in payload:
        amount_rub = int(payload["amount_rub"])
    else:
        # обратная конверсия: ₽ = ⭐ / STARS_PER_RUB
        amount_rub = int(
            (Decimal(stars) / Decimal(str(STARS_PER_RUB))).to_integral_value(rounding=ROUND_HALF_UP)
        )

    if amount_rub <= 0:
        await message.answer("❌ Не удалось определить сумму оплаты.", reply_markup=close())
        return

    # Реферальное начисление (если настроено)
    referral_id = get_user_referral(user_id)
    if referral_id and TgConfig.REFERRAL_PERCENT:
        try:
            referral_operation = int(
                Decimal(TgConfig.REFERRAL_PERCENT) / Decimal(100) * Decimal(amount_rub)
            )
            if referral_operation > 0:
                update_balance(referral_id, referral_operation)
                await message.bot.send_message(
                    referral_id,
                    f'✅ Вы получили {referral_operation}₽ от вашего реферала {message.from_user.first_name}',
                    reply_markup=close()
                )
        except Exception:
            pass

    # Фиксируем операцию и пополняем баланс
    current_time = datetime.datetime.now()
    create_operation(user_id, amount_rub, current_time)
    update_balance(user_id, amount_rub)

    await message.answer(
        f'✅ Баланс пополнен на {amount_rub}₽ (Telegram Stars)',
        reply_markup=back('profile')
    )


# --- Хэндлер: покупка товара
@router.callback_query(F.data.startswith('buy_'))
async def buy_item_callback_handler(call: CallbackQuery):
    """
    Покупка товара пользователем.
    """
    item_name = call.data[4:]
    user_id = call.from_user.id

    item_info = get_item_info(item_name)
    if not item_info:
        await call.answer("❌ Товар не найден", show_alert=True)
        return

    price = int(item_info["price"])
    balance = get_user_balance(user_id) or 0
    if balance < price:
        await call.message.edit_text(
            '❌ Недостаточно средств',
            reply_markup=back(f'item_{item_name}')
        )
        return

    value_data = get_item_value(item_name)
    if not value_data:
        await call.message.edit_text(
            '❌ Товара нет в наличии',
            reply_markup=back(f'item_{item_name}')
        )
        return

    buy_item(value_data['id'], value_data['is_infinity'])

    add_bought_item(
        value_data['item_name'],
        value_data['value'],
        price,
        user_id,
        datetime.datetime.now()
    )

    new_balance = buy_item_for_balance(user_id, price)

    await call.message.edit_text(
        f'✅ Товар куплен. '
        f'<b>Баланс</b>: <i>{new_balance}</i>₽\n\n{value_data["value"]}',
        parse_mode='HTML',
        reply_markup=back(f'item_{item_name}')
    )

    # тихо залогируем покупку
    try:
        user_info = await call.bot.get_chat(user_id)
        audit_logger.info(
            f"Пользователь {user_id} ({user_info.first_name}) "
            f"купил 1 товар позиции {value_data['item_name']} за {price}р"
        )
    except Exception:
        pass
