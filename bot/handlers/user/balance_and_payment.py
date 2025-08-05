import asyncio
import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.database.methods import get_item_info, get_user_balance, get_item_value, buy_item, add_bought_item, \
    buy_item_for_balance, start_operation, \
    select_unfinished_operations, get_user_referral, finish_operation, update_balance, create_operation
from bot.handlers.other import get_bot_user_ids
from bot.keyboards import back, payment_menu, close, get_payment_choice
from bot.logger_mesh import logger
from bot.misc import TgConfig, EnvKeys
from bot.misc.payment import quick_pay, check_payment_status, CryptoPayAPI


async def replenish_balance_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    message_id = call.message.message_id

    if EnvKeys.ACCESS_TOKEN and EnvKeys.ACCOUNT_NUMBER is not None:
        TgConfig.STATE[f'{user_id}_message_id'] = message_id
        TgConfig.STATE[user_id] = 'replenish_balance_choice'
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=message_id,
                                    text='💰 Введите сумму для пополнения:',
                                    reply_markup=back('profile'))
        return

    await call.answer('Пополнение не было настроено')


async def replenish_balance_choice(message: Message):
    bot, user_id = await get_bot_user_ids(message)

    text = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if not text.isdigit() or int(text) < 5 or int(text) > 10000:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text="❌ Неверная сумма пополнения. "
                                         "Сумма пополнения должна быть числом не меньше 20₽ и не более 10 000₽",
                                    reply_markup=back('replenish_balance'))
        return

    TgConfig.STATE[f'{user_id}_sum'] = text
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text=f'💳 Выберите способ оплаты',
                                reply_markup=get_payment_choice())


async def process_replenish_balance(call: CallbackQuery, state: FSMContext):
    bot, user_id = await get_bot_user_ids(call)

    amount = TgConfig.STATE.get(f'{user_id}_sum')
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None

    sleep = TgConfig.PAYMENT_TIME
    sleep_time = int(sleep)

    if call.data == "pay_cryptopay":
        if EnvKeys.CRYPTO_PAY_TOKEN is None:
            await call.answer("❌ Метод не был добавлен")
            return
        crypto = CryptoPayAPI()
        invoice = await crypto.create_invoice(
            amount=float(amount),
            currency="RUB",
            accepted_assets="TON,USDT,BTC,ETH",
            payload=str(user_id),
            expires_in=TgConfig.PAYMENT_TIME
        )
        pay_url = invoice.get("mini_app_invoice_url")
        invoice_id = invoice.get("invoice_id")

        await state.update_data(invoice_id=invoice_id, payment_type="cryptopay")
        start_operation(user_id, amount, invoice_id)
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=message_id,
            text=f"💵 Сумма пополнения: {amount}₽.\n"
                 f"⌛️ У вас имеется {int(sleep_time / 60)} минут на оплату.\n"
                 f"<b>❗️ После оплаты нажмите кнопку «Проверить оплату»</b>",
            reply_markup=payment_menu(pay_url)
        )
        await asyncio.sleep(sleep_time)
        info = select_unfinished_operations(invoice_id)
        if info:
            payment_status = await check_payment_status(invoice_id)

            if not payment_status == "success":
                finish_operation(invoice_id)
    else:
        if EnvKeys.ACCOUNT_NUMBER is None or EnvKeys.ACCESS_TOKEN is None:
            await call.answer("❌ Метод не был добавлен")
            return
        label, url = quick_pay(amount, user_id)
        start_operation(user_id, amount, label)
        markup = payment_menu(url)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=message_id,
                                    text=f'💵 Сумма пополнения: {amount}₽.\n'
                                         f'⌛️ У вас имеется {int(sleep_time / 60)} минут на оплату.\n'
                                         f'<b>❗️ После оплаты нажмите кнопку «Проверить оплату»</b>',
                                    reply_markup=markup)
        await state.update_data(label=label, payment_type="yoomoney")
        await asyncio.sleep(sleep_time)
        info = select_unfinished_operations(label)
        if info:
            payment_status = await check_payment_status(label)

            if not payment_status == "success":
                finish_operation(label)


async def checking_payment(call: CallbackQuery, state: FSMContext):
    bot, user_id = await get_bot_user_ids(call)
    message_id = call.message.message_id

    data = await state.get_data()
    payment_type = data.get("payment_type")

    if payment_type == "cryptopay":
        invoice_id = data.get("invoice_id")
        crypto = CryptoPayAPI()
        info = await crypto.get_invoice(invoice_id)
        status = info.get("status")
        if status == "paid":
            balance_amount = int(info.get("balance_amount"))
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            referral_id = get_user_referral(user_id)
            finish_operation(invoice_id)

            if referral_id and TgConfig.REFERRAL_PERCENT != 0:
                referral_percent = TgConfig.REFERRAL_PERCENT
                referral_operation = round((referral_percent / 100) * balance_amount)
                update_balance(referral_id, referral_operation)
                await bot.send_message(referral_id,
                                       f'✅ Вы получили {referral_operation}₽ '
                                       f'от вашего реферал {call.from_user.first_name}',
                                       reply_markup=close())

            create_operation(user_id, balance_amount, formatted_time)
            update_balance(user_id, balance_amount)
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=message_id,
                                        text=f'✅ Баланс пополнен на {balance_amount}₽',
                                        reply_markup=back('profile'))
        elif status == "active":
            await call.answer("❌ Платёж ещё не оплачен.")
        else:
            await call.answer("❌ Срок действия счёта истёк.")

    elif payment_type == "yoomoney":

        label = data.get("label")
        info = select_unfinished_operations(label)

        if info:
            operation_value = info[0]
            payment_status = await check_payment_status(label)

            if payment_status == "success":
                current_time = datetime.datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                referral_id = get_user_referral(user_id)
                finish_operation(label)

                if referral_id and TgConfig.REFERRAL_PERCENT != 0:
                    referral_percent = TgConfig.REFERRAL_PERCENT
                    referral_operation = round((referral_percent / 100) * operation_value)
                    update_balance(referral_id, referral_operation)
                    await bot.send_message(referral_id,
                                           f'✅ Вы получили {referral_operation}₽ '
                                           f'от вашего реферал {call.from_user.first_name}',
                                           reply_markup=close())

                create_operation(user_id, operation_value, formatted_time)
                update_balance(user_id, operation_value)
                await bot.edit_message_text(chat_id=call.message.chat.id,
                                            message_id=message_id,
                                            text=f'✅ Баланс пополнен на {operation_value}₽',
                                            reply_markup=back('profile'))
            else:
                await call.answer(text='❌ Оплата не прошла успешно')
        else:
            await call.answer(text='❌ Счет не найден')


async def buy_item_callback_handler(call: CallbackQuery):
    item_name = call.data[4:]
    bot, user_id = await get_bot_user_ids(call)
    msg = call.message.message_id
    item_info_list = get_item_info(item_name)
    item_price = item_info_list["price"]
    user_balance = get_user_balance(user_id)

    if user_balance >= item_price:
        value_data = get_item_value(item_name)

        if value_data:
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            buy_item(value_data['id'], value_data['is_infinity'])
            add_bought_item(value_data['item_name'], value_data['value'], item_price, user_id, formatted_time)
            new_balance = buy_item_for_balance(user_id, item_price)
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=msg,
                                        text=f'✅ Товар куплен. '
                                             f'<b>Баланс</b>: <i>{new_balance}</i>₽\n\n{value_data["value"]}',
                                        parse_mode='HTML',
                                        reply_markup=back(f'item_{item_name}'))
            user_info = await bot.get_chat(user_id)
            logger.info(f"Пользователь {user_id} ({user_info.first_name})"
                        f" купил 1 товар позиции {value_data['item_name']} за {item_price}р")
            return

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=msg,
                                    text='❌ Товара нет в  наличие',
                                    reply_markup=back(f'item_{item_name}'))
        return

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=msg,
                                text='❌ Недостаточно средств',
                                reply_markup=back(f'item_{item_name}'))


def register_balance_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(replenish_balance_callback_handler,
                                       lambda c: c.data == 'replenish_balance')
    dp.register_callback_query_handler(checking_payment,
                                       lambda c: c.data == 'check')

    dp.register_callback_query_handler(process_replenish_balance,
                                       text=["pay_yoomoney", "pay_cryptopay"])

    dp.register_message_handler(replenish_balance_choice,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'replenish_balance_choice')


    dp.register_callback_query_handler(buy_item_callback_handler,
                                       lambda c: c.data.startswith('buy_'))
