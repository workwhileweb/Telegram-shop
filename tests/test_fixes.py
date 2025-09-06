import asyncio
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime


# === TRANSACTIONAL BUYING TEST ===

@pytest.mark.asyncio
async def test_concurrent_purchase_safety():
    """Test: only one user has to buy the last product"""

    from bot.database.methods import buy_item_transaction
    from bot.database import Database
    from bot.database.models import User, Goods, ItemValues, Categories

    # Preparing test data
    with Database().session() as s:
        # Create test users
        user1 = User(telegram_id=111, balance=Decimal("1000"),
                     registration_date=datetime.now(), role_id=1)
        user2 = User(telegram_id=222, balance=Decimal("1000"),
                     registration_date=datetime.now(), role_id=1)
        s.add(user1)
        s.add(user2)

        # Create category and product
        category = Categories(name="test_category")
        s.add(category)

        goods = Goods(
            "test_item",
            Decimal("100"),
            "Test",
            "test_category"
        )
        s.add(goods)

        # Add ONLY ONE item
        item_value = ItemValues(name="test_item", value="SECRET_KEY", is_infinity=False)
        s.add(item_value)

        s.commit()

    # Parallel buying
    async def buy_user1():
        await asyncio.sleep(0.01)  # A slight delay
        return buy_item_transaction(111, "test_item")

    async def buy_user2():
        return buy_item_transaction(222, "test_item")

    # Run at the same time
    results = await asyncio.gather(buy_user1(), buy_user2(), return_exceptions=True)

    # Check the results
    success_count = sum(1 for r in results if not isinstance(r, Exception) and r[0])
    failed_count = sum(1 for r in results if not isinstance(r, Exception) and not r[0])

    assert success_count == 1, "Only one must successfully buy"
    assert failed_count == 1, "One should get an error"

    # Check error messages
    for result in results:
        if not isinstance(result, Exception) and not result[0]:
            assert result[1] in ["out_of_stock", "transaction_error"], \
                f"Unexpected mistake: {result[1]}"

    # Cleansing
    with Database().session() as s:
        s.query(User).filter(User.telegram_id.in_([111, 222])).delete()
        s.query(Goods).filter(Goods.name == "test_item").delete()
        s.query(Categories).filter(Categories.name == "test_category").delete()
        s.commit()

    print("✅ Transactional shopping security test passed")


# === PAYMENT IDEMPOTENCY TEST ===

@pytest.mark.asyncio
async def test_payment_idempotency():
    """Test: payment re-processing should not duplicate accruals"""

    from bot.database.methods import process_payment_with_referral
    from bot.database import Database
    from bot.database.models import User, Payments

    # Preparation
    with Database().session() as s:
        user = User(telegram_id=333, balance=Decimal("0"),
                    registration_date=datetime.now(), role_id=1)
        s.add(user)
        s.commit()

    # First attempt to process the payment
    result1 = process_payment_with_referral(
        user_id=333,
        amount=Decimal("500"),
        provider="test",
        external_id="payment_123",
        referral_percent=0
    )

    # A second attempt with the same external_id
    result2 = process_payment_with_referral(
        user_id=333,
        amount=Decimal("500"),
        provider="test",
        external_id="payment_123",  # Same ID!
        referral_percent=0
    )

    assert result1[0] == True, "The first payment has to go through"
    assert result2[0] == False, "The second payment should be rejected"
    assert result2[1] == "already_processed", "There should be a duplicate message"

    # Check balance - should be only 500, not 1000
    with Database().session() as s:
        user = s.query(User).filter(User.telegram_id == 333).one()
        assert user.balance == Decimal("500"), f"The balance should be 500, not {user.balance}"

        # Checking the payment records
        payments = s.query(Payments).filter(Payments.external_id == "payment_123").all()
        assert len(payments) == 1, "There should only be one payment record"

        # Cleansing
        s.query(User).filter(User.telegram_id == 333).delete()
        s.query(Payments).filter(Payments.external_id == "payment_123").delete()
        s.commit()

    print("✅ Payment idempotency test passed")


# === ТЕСТ RATE LIMITING ===

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test: check rate limiting"""

    from bot.middleware import RateLimiter, RateLimitConfig

    config = RateLimitConfig(
        global_limit=5,  # 5 requests
        global_window=10,  # in 10 seconds
        ban_duration=5,  # ban for 5 seconds
        action_limits={
            'test_action': (2, 10)  # 2 times in 10 seconds
        }
    )

    limiter = RateLimiter(config)
    user_id = 444

    # Global Limit Test
    for i in range(5):
        assert limiter.check_global_limit(user_id), f"Query {i + 1} must pass"

    assert not limiter.check_global_limit(user_id), "The 6th request must be blocked"

    # Action limit test
    limiter2 = RateLimiter(config)
    user_id2 = 555

    assert limiter2.check_action_limit(user_id2, 'test_action'), "The 1st action request must pass"
    assert limiter2.check_action_limit(user_id2, 'test_action'), "The 2nd request for action must pass"
    assert not limiter2.check_action_limit(user_id2, 'test_action'), "The 3rd request must be blocked"

    # Test ban
    for i in range(6):
        limiter.check_global_limit(user_id)

    limiter.ban_user(user_id)
    assert limiter.is_banned(user_id), "The user should be banned"

    wait_time = limiter.get_wait_time(user_id)
    assert 0 < wait_time <= 5, f"The wait time should be between 0 and 5 sec, received: {wait_time}"

    print("✅ Rate Limiting test passed")


# === ENHANCED MAILING TEST ===

@pytest.mark.asyncio
async def test_broadcast_manager():
    """Test: testing batch mailing"""

    from bot.misc import BroadcastManager, BroadcastStats
    from aiogram.exceptions import TelegramForbiddenError
    from aiogram.methods import SendMessage  # For the correct type of exception

    # Mock bot
    bot_mock = AsyncMock()
    bot_mock.send_message = AsyncMock()

    # Customization: some users have blocked the bot
    async def send_side_effect(chat_id, **kwargs):
        if chat_id in [3, 7]:  # These users have blocked
            method = SendMessage(chat_id=chat_id, text=kwargs.get("text", ""))
            raise TelegramForbiddenError(method=method, message="Forbidden: bot was blocked by the user")
        return MagicMock()

    bot_mock.send_message.side_effect = send_side_effect

    manager = BroadcastManager(
        bot=bot_mock,
        batch_size=3,  # Small batch for the test
        batch_delay=0.01,  # Minimum delay
        retry_count=1
    )

    # User list
    user_ids = list(range(1, 11))  # 10 users

    # Progress counter: asynchronous function
    progress_calls = []

    async def progress_callback(statistic: BroadcastStats):
        progress_calls.append(statistic.sent + statistic.failed)

    # Start the mailing
    stats = await manager.broadcast(
        user_ids=user_ids,
        text="Test message",
        progress_callback=progress_callback  # Now the correct type
    )

    # Проверяем результаты
    assert stats.total == 10, "There must be a total of 10 users."
    assert stats.sent == 8, "8 should get (2 blocked)."
    assert stats.failed == 2, "2 must fail."
    assert stats.success_rate == 80.0, "Success rate should be 80%."
    assert stats.duration is not None, "There must be a run time."
    assert len(progress_calls) > 0, "There must be challenges to progress."

    # Check batching (there should be 4 batches: 3+3+3+1)
    call_count = bot_mock.send_message.call_count
    assert call_count == 10, f"There must have been 10 calls, received {call_count}"

    print("✅ The improved mailing test has passed")


# === LAZY PAGINATION TEST ===

@pytest.mark.asyncio
async def test_lazy_pagination():
    """Test: testing lazy pagination loading"""

    from bot.misc import LazyPaginator

    # Mock request function
    call_counter = {"count": 0}

    async def mock_query(offset=0, limit=10, count_only=False):
        call_counter["count"] += 1

        if count_only:
            return 100  # 100 items in total

        # Return the fake data
        return [f"item_{i}" for i in range(offset, min(offset + limit, 100))]

    paginator = LazyPaginator(
        query_func=mock_query,
        per_page=10,
        cache_pages=3
    )

    # We get the first page
    page1 = await paginator.get_page(0)
    assert len(page1) == 10, "The first page must contain 10 items"
    assert page1[0] == "item_0", "The first item must be item_0"

    # Re-request the first page (must be taken from the cache)
    calls_before = call_counter["count"]
    page1_cached = await paginator.get_page(0)
    assert call_counter["count"] == calls_before, "There must be no new request (cache)"
    assert page1 == page1_cached, "The data must be the same."

    # Request another page
    page5 = await paginator.get_page(5)
    assert len(page5) == 10, "The 5th page must contain 10 elements"
    assert page5[0] == "item_50", "The first item on page 5 must be item_50"

    # Checking the total quantity
    total = await paginator.get_total_count()
    assert total == 100, "The total quantity should be 100"

    # Checking to clear the cache
    paginator.clear_cache()
    assert len(paginator._cache) == 0, "Cache should be cleared"

    print("✅ Lazy pagination test passed")


# === MAIN FUNCTION TO RUN TESTS ===

async def run_all_tests():
    """Run all tests"""
    print("run tests")
    print("=" * 50)

    try:
        print("\n1. Shopping transaction security testing...")
        await test_concurrent_purchase_safety()
    except Exception as e:
        print(f"❌ Error: {e}")

    try:
        print("\n2. Testing payment idempotency...")
        await test_payment_idempotency()
    except Exception as e:
        print(f"❌ Error: {e}")

    try:
        print("\n3. Testing Rate Limiting...")
        await test_rate_limiting()
    except Exception as e:
        print(f"❌ Error: {e}")

    try:
        print("\n4. Testing Enhanced Mailing...")
        await test_broadcast_manager()
    except Exception as e:
        print(f"❌ Error: {e}")

    try:
        print("\n5. Testing lazy pagination...")
        await test_lazy_pagination()
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
