import json
import datetime
from decimal import Decimal, ROUND_HALF_UP

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, SuccessfulPayment
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from bot.database.methods import (
    get_user_balance, get_item_info, get_item_value, buy_item, add_bought_item,
    buy_item_for_balance,
    get_user_referral, update_balance, create_operation, mark_payment_succeeded, create_pending_payment,
    ensure_payment_succeeded
)
from bot.keyboards import back, payment_menu, close, get_payment_choice
from bot.logger_mesh import audit_logger
from bot.misc import EnvKeys
from bot.handlers.other import _any_payment_method_enabled
from bot.misc.payment import CryptoPayAPI, send_stars_invoice, send_fiat_invoice
from bot.filters import ValidAmountFilter
from bot.i18n import localize
from bot.states import BalanceStates

router = Router()


# --- Start top-up
@router.callback_query(F.data == "replenish_balance")
async def replenish_balance_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Ask user for the amount if at least one payment method is enabled.
    """
    if not _any_payment_method_enabled():
        await call.answer(localize("payments.not_configured"), show_alert=True)
        return

    await call.message.edit_text(
        localize("payments.replenish_prompt", currency=EnvKeys.PAY_CURRENCY),
        reply_markup=back('profile')
    )
    await state.set_state(BalanceStates.waiting_amount)


# --- Amount entered (valid)
@router.message(BalanceStates.waiting_amount, ValidAmountFilter())
async def replenish_balance_amount(message: Message, state: FSMContext):
    """
    Store amount and show payment methods.
    """
    amount = int(message.text)
    await state.update_data(amount=amount)

    await message.answer(
        localize("payments.method_choose"),
        reply_markup=get_payment_choice()
    )
    await state.set_state(BalanceStates.waiting_payment)


# --- Amount entered (invalid)
@router.message(BalanceStates.waiting_amount)
async def invalid_amount(message: Message, state: FSMContext):
    """
    Tell user the amount is invalid.
    """
    await message.answer(
        localize("payments.replenish_invalid", min_amount=EnvKeys.MIN_AMOUNT, max_amount=EnvKeys.MAX_AMOUNT,
                 currency=EnvKeys.PAY_CURRENCY),
        reply_markup=back('replenish_balance')
    )


# --- Payment method chosen
@router.callback_query(
    BalanceStates.waiting_payment,
    F.data.in_(["pay_cryptopay", "pay_stars", "pay_fiat"])
)
async def process_replenish_balance(call: CallbackQuery, state: FSMContext):
    """
    Create an invoice for the chosen payment method.
    For Stars/Fiat we send Telegram invoice (then pre_checkout/success handlers fire).
    """
    data = await state.get_data()
    amount = data.get('amount')
    if amount is None:
        await call.answer(localize("payments.session_expired"), show_alert=True)
        await call.message.edit_text(localize("menu.title"), reply_markup=back('back_to_menu'))
        await state.clear()
        return

    amount_dec = Decimal(amount).quantize(Decimal("1."), rounding=ROUND_HALF_UP)
    ttl_seconds = int(EnvKeys.PAYMENT_TIME)

    if call.data == "pay_cryptopay":
        # Crypto Bot
        if not EnvKeys.CRYPTO_PAY_TOKEN:
            await call.answer(localize("payments.not_configured"), show_alert=True)
            return
        try:
            crypto = CryptoPayAPI()
            invoice = await crypto.create_invoice(
                amount=float(amount_dec),
                currency=EnvKeys.PAY_CURRENCY,
                accepted_assets="TON,USDT,BTC,ETH",
                payload=str(call.from_user.id),
                expires_in=EnvKeys.PAYMENT_TIME
            )
        except Exception as e:
            await call.answer(localize("payments.crypto.create_fail", error=str(e)), show_alert=True)
            return

        pay_url = invoice.get("mini_app_invoice_url")
        invoice_id = invoice.get("invoice_id")

        await state.update_data(invoice_id=invoice_id, payment_type="cryptopay")

        await call.message.edit_text(
            localize("payments.invoice.summary",
                     amount=int(amount_dec),
                     minutes=int(ttl_seconds / 60),
                     button=localize("btn.check_payment"),
                     currency=EnvKeys.PAY_CURRENCY),
            reply_markup=payment_menu(pay_url)
        )

    elif call.data == "pay_stars":
        # Telegram Stars (XTR)
        if EnvKeys.STARS_PER_VALUE > 0:
            try:
                await send_stars_invoice(
                    bot=call.message.bot,
                    chat_id=call.from_user.id,
                    amount=int(amount_dec),
                )
            except Exception as e:
                await call.answer(localize("payments.stars.create_fail", error=str(e)), show_alert=True)
                return

            await state.clear()
        else:
            await call.answer(localize("payments.not_configured"), show_alert=True)
            return

    elif call.data == "pay_fiat":
        # Telegram Payments (fiat provider)
        if not EnvKeys.TELEGRAM_PROVIDER_TOKEN:
            await call.answer(localize("payments.not_configured"), show_alert=True)
            return

        try:
            await send_fiat_invoice(
                bot=call.message.bot,
                chat_id=call.from_user.id,
                amount=int(amount_dec),
            )
        except Exception as e:
            await call.answer(localize("payments.fiat.create_fail", error=str(e)), show_alert=True)
            return
        await state.clear()


# --- Manual payment check (CryptoPay)
@router.callback_query(F.data == "check")
async def checking_payment(call: CallbackQuery, state: FSMContext):
    """
    Check CryptoPay invoice status and credit balance if paid.
    """
    user_id = call.from_user.id
    data = await state.get_data()
    payment_type = data.get("payment_type")

    if not payment_type:
        await call.answer(localize("payments.no_active_invoice"), show_alert=True)
        return

    if payment_type == "cryptopay":
        invoice_id = data.get("invoice_id")
        if not invoice_id:
            await call.answer(localize("payments.invoice_not_found"), show_alert=True)
            await state.clear()
            return

        try:
            crypto = CryptoPayAPI()
            info = await crypto.get_invoice(invoice_id)
        except Exception as e:
            await call.answer(localize("payments.crypto.create_fail", error=str(e)), show_alert=True)
            return

        status = info.get("status")
        if status == "paid":
            balance_amount = int(Decimal(str(info.get("amount", "0"))).quantize(Decimal("1.")))
            referral_id = get_user_referral(user_id)

            if referral_id and EnvKeys.REFERRAL_PERCENT:
                try:
                    referral_operation = int(
                        Decimal(EnvKeys.REFERRAL_PERCENT) / Decimal(100) * Decimal(balance_amount)
                    )
                    update_balance(referral_id, referral_operation)
                    await call.bot.send_message(
                        referral_id,
                        localize('payments.referral.bonus',
                                 amount=referral_operation,
                                 name=call.from_user.first_name,
                                 currency=EnvKeys.PAY_CURRENCY),
                        reply_markup=close()
                    )
                except Exception:
                    pass

            status = ensure_payment_succeeded("cryptopay", str(invoice_id), user_id, balance_amount,
                                              EnvKeys.PAY_CURRENCY)
            if status == "already":
                await call.answer(localize("payments.already_processed"), show_alert=True)
                return

            create_operation(user_id, balance_amount, datetime.datetime.now())
            update_balance(user_id, balance_amount)

            await call.message.edit_text(
                localize("payments.topped_simple", amount=balance_amount, currency=EnvKeys.PAY_CURRENCY),
                reply_markup=back('profile')
            )
            await state.clear()

            # audit log
            try:
                user_info = await call.bot.get_chat(user_id)
                audit_logger.info(
                    f"user {user_id} ({user_info.first_name}) "
                    f"replenished the balance by: {balance_amount} {EnvKeys.PAY_CURRENCY} ({payment_type})"
                )
            except Exception:
                pass

        elif status == "active":
            await call.answer(localize("payments.not_paid_yet"))
        else:
            await call.answer(localize("payments.expired"), show_alert=True)


# --- Telegram Payments pre-checkout
@router.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery):
    """Telegram requires answering ok=True before payment proceeds. Also register pending payment."""
    try:
        payload = json.loads(query.invoice_payload or "{}")
    except Exception:
        payload = {}
    amount = int(payload.get("amount", 0))
    if amount > 0:
        pass
    await query.answer(ok=True)


# --- Successful Telegram payment (Stars / Fiat)
@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """
    Handle successful payment:
    - XTR (Stars): total_amount is ⭐. We take RUB from payload (amount) or convert ⭐ → ₽.
    - Fiat: total_amount is minor units; divide by 100 (or 1 for JPY/KRW).
    """
    sp: SuccessfulPayment = message.successful_payment
    user_id = message.from_user.id

    payload = {}
    try:
        if sp.invoice_payload:
            payload = json.loads(sp.invoice_payload)
    except Exception:
        payload = {}

    amount = 0

    if sp.currency == "XTR":
        # Stars
        if "amount" in payload:
            amount = int(payload["amount"])
        else:
            amount = int(
                (Decimal(int(sp.total_amount)) / Decimal(str(EnvKeys.STARS_PER_VALUE)))
                .to_integral_value(rounding=ROUND_HALF_UP)
            )
    else:
        # Fiat
        currency = sp.currency.upper()
        multiplier = 1 if currency in {"JPY", "KRW"} else 100
        amount = int(Decimal(sp.total_amount) / Decimal(multiplier))

    if amount <= 0:
        await message.answer(localize("payments.unable_determine_amount"), reply_markup=close())
        return

    # Idempotence
    provider = "telegram" if sp.currency != "XTR" else "stars"
    external_id = sp.telegram_payment_charge_id or sp.provider_payment_charge_id or f"{provider}:{user_id}:{sp.total_amount}"

    # try to mark the payment as "succeeded". If there is no entry, create pending->succeeded within one transaction.
    try:
        ok = mark_payment_succeeded(provider, external_id)
        if not ok:

            try:
                create_pending_payment(provider, external_id, user_id, amount, sp.currency)
            except IntegrityError:
                pass
            ok = mark_payment_succeeded(provider, external_id)

        if not ok:
            # by this point, it's definitely "already processed"
            await message.answer(localize("payments.already_processed"), reply_markup=close())
            return
    except Exception:
        await message.answer(localize("payments.processing_error"), reply_markup=close())

    # Referral bonus (if configured)
    referral_id = get_user_referral(user_id)
    if referral_id and EnvKeys.REFERRAL_PERCENT:
        try:
            referral_operation = int(
                Decimal(EnvKeys.REFERRAL_PERCENT) / Decimal(100) * Decimal(amount)
            )
            if referral_operation > 0:
                update_balance(referral_id, referral_operation)
                await message.bot.send_message(
                    referral_id,
                    localize('payments.referral.bonus',
                             amount=referral_operation,
                             currency=EnvKeys.PAY_CURRENCY,
                             name=message.from_user.first_name),
                    reply_markup=close()
                )
        except Exception:
            pass

    # Persist operation & credit balance
    current_time = datetime.datetime.now()
    create_operation(user_id, amount, current_time)
    update_balance(user_id, amount)

    suffix = localize("payments.success_suffix.stars") if sp.currency == "XTR" else localize(
        "payments.success_suffix.tg")
    await message.answer(
        localize('payments.topped_with_suffix', amount=amount, suffix=suffix, currency=EnvKeys.PAY_CURRENCY),
        reply_markup=back('profile')
    )
    # audit log
    try:
        user_info = await message.bot.get_chat(user_id)
        audit_logger.info(
            f"user {user_id} ({user_info.first_name}) "
            f"replenished the balance by: {amount} {EnvKeys.PAY_CURRENCY} ({suffix})"
        )
    except Exception:
        pass


# --- Buy an item
@router.callback_query(F.data.startswith('buy_'))
async def buy_item_callback_handler(call: CallbackQuery):
    """
    Handle product purchase with balance.
    """
    item_name = call.data[4:]
    user_id = call.from_user.id

    item_info = get_item_info(item_name)
    if not item_info:
        await call.answer(localize("shop.item.not_found"), show_alert=True)
        return

    price = int(item_info["price"])
    balance = get_user_balance(user_id) or 0
    if balance < price:
        await call.message.edit_text(
            localize("shop.insufficient_funds"),
            reply_markup=back(f'item_{item_name}')
        )
        return

    value_data = get_item_value(item_name)
    if not value_data:
        await call.message.edit_text(
            localize("shop.out_of_stock"),
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
        localize('shop.purchase.success', balance=new_balance, value=value_data["value"],
                 currency=EnvKeys.PAY_CURRENCY),
        parse_mode='HTML',
        reply_markup=back(f'item_{item_name}')
    )

    # audit log
    try:
        user_info = await call.bot.get_chat(user_id)
        audit_logger.info(
            f"user {user_id} ({user_info.first_name}) "
            f"bought 1 item from position: {value_data['item_name']} for {price} {EnvKeys.PAY_CURRENCY}"
        )
    except Exception:
        pass
