from datetime import datetime
from decimal import Decimal
from random import randint

from bot.database.models import User, ItemValues, Goods, BoughtGoods, Payments, Operations
from bot.database import Database
from bot.misc import EnvKeys


def buy_item_transaction(telegram_id: int, item_name: str) -> tuple[bool, str, dict | None]:
    """
    Complete transactional purchase of goods with checks and locks.
    Returns: (success, message, purchase_data)
    """
    with Database().session() as s:
        try:
            # Starting the transaction
            s.begin()

            # 1. Block the user to check the balance
            user = s.query(User).filter(
                User.telegram_id == telegram_id
            ).with_for_update().one_or_none()

            if not user:
                s.rollback()
                return False, "user_not_found", None

            # 2. Get information about the product
            goods = s.query(Goods).filter(
                Goods.name == item_name
            ).with_for_update().one_or_none()

            if not goods:
                s.rollback()
                return False, "item_not_found", None

            price = Decimal(str(goods.price))

            # 3. Checking the balance
            if user.balance < price:
                s.rollback()
                return False, "insufficient_funds", None

            # 4. receive and block the goods for purchase
            item_value = s.query(ItemValues).filter(
                ItemValues.item_name == item_name
            ).with_for_update(skip_locked=True).first()

            if not item_value:
                s.rollback()
                return False, "out_of_stock", None

            # 5. If the product is not endless, we remove it
            if not item_value.is_infinity:
                s.delete(item_value)

            # 6. Write off the balance
            user.balance -= price

            # 7. Create a purchase record
            bought_item = BoughtGoods(
                name=item_name,
                value=item_value.value,
                price=price,
                buyer_id=telegram_id,
                bought_datetime=datetime.now(),
                unique_id=str(randint(1_000_000_000, 9_999_999_999))
            )
            s.add(bought_item)

            # 8. Commit the transaction
            s.commit()

            return True, "success", {
                "item_name": item_name,
                "value": item_value.value,
                "price": float(price),
                "new_balance": float(user.balance),
                "unique_id": bought_item.unique_id
            }

        except Exception as e:
            s.rollback()
            return False, f"transaction_error: {str(e)}", None


def process_payment_with_referral(
        user_id: int,
        amount: Decimal,
        provider: str,
        external_id: str,
        referral_percent: int = 0
) -> tuple[bool, str]:
    """
    Processing a payment with a referral bonus in one transaction.
    Returns (success, message)
    """

    with Database().session() as s:
        try:
            s.begin()

            # 1. Check the idempotency of the payment
            existing_payment = s.query(Payments).filter(
                Payments.provider == provider,
                Payments.external_id == external_id
            ).with_for_update().first()

            if existing_payment:
                if existing_payment.status == "succeeded":
                    s.rollback()
                    return False, "already_processed"
                existing_payment.status = "succeeded"
            else:
                # Create a new payment record
                payment = Payments(
                    provider=provider,
                    external_id=external_id,
                    user_id=user_id,
                    amount=amount,
                    currency=EnvKeys.PAY_CURRENCY,
                    status="succeeded"
                )
                s.add(payment)

            # 2. Update the user's balance
            user = s.query(User).filter(
                User.telegram_id == user_id
            ).with_for_update().one()

            user.balance += amount

            # 3. Create a transaction record
            operation = Operations(
                user_id=user_id,
                operation_value=amount,
                operation_time=datetime.now()
            )
            s.add(operation)

            # 4. Process the referral bonus
            if referral_percent > 0 and user.referral_id:
                referral_amount = (Decimal(referral_percent) / Decimal(100)) * amount

                if referral_amount > 0:
                    # Update the referrer's balance
                    referrer = s.query(User).filter(
                        User.telegram_id == user.referral_id
                    ).with_for_update().one_or_none()

                    if referrer:
                        referrer.balance += referral_amount

                        # Create a referral credit record
                        from bot.database.models import ReferralEarnings
                        earning = ReferralEarnings(
                            referrer_id=user.referral_id,
                            referral_id=user_id,
                            amount=referral_amount,
                            original_amount=amount
                        )
                        s.add(earning)

            s.commit()
            return True, "success"

        except Exception as e:
            s.rollback()
            return False, f"error: {str(e)}"
