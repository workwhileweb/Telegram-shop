from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.database.methods import (
    check_user_referrals, get_user_referrals_list, get_referral_earnings_from_user,
    get_all_referral_earnings, get_referral_earnings_stats, get_one_referral_earning,
)
from bot.handlers.other import get_bot_info
from bot.keyboards import back, referral_system_keyboard, paginated_keyboard
from bot.misc import EnvKeys
from bot.i18n import localize

router = Router()


# Referral system
@router.callback_query(F.data == "referral_system")
async def referral_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Show referral info, personal invite link, and additional buttons.
    """
    user_id = call.from_user.id
    referrals_count = check_user_referrals(user_id)
    referral_percent = EnvKeys.REFERRAL_PERCENT
    bot_username = await get_bot_info(call)

    earnings_stats = get_referral_earnings_stats(user_id)

    has_referrals = referrals_count > 0
    has_earnings = earnings_stats['total_earnings_count'] > 0

    text = (
        f"{localize('referral.title')}\n"
        f"{localize('referral.link', bot_username=bot_username, user_id=user_id)}\n"
        f"{localize('referral.count', count=referrals_count)}\n"
        f"{localize('referral.description', percent=referral_percent)}"
    )

    if has_earnings:
        text += "\n\n" + localize('referrals.stats.template',
                                  active_count=earnings_stats['active_referrals_count'],
                                  total_earned=int(earnings_stats['total_amount']),
                                  total_original=int(earnings_stats['total_original_amount']),
                                  earnings_count=earnings_stats['total_earnings_count'],
                                  currency=EnvKeys.PAY_CURRENCY
                                  )

    markup = referral_system_keyboard(has_referrals, has_earnings)
    await call.message.edit_text(text, reply_markup=markup)
    await state.clear()


# List of referrals
@router.callback_query(F.data == "view_referrals")
async def view_referrals_handler(call: CallbackQuery, state: FSMContext):
    """
    Show a list of all user referrals.
    """
    user_id = call.from_user.id
    referrals = get_user_referrals_list(user_id)

    if not referrals:
        await call.message.edit_text(
            localize("referrals.list.empty"),
            reply_markup=back("referral_system")
        )
        return

    markup = paginated_keyboard(
        items=referrals,
        item_text=lambda referral_data: localize("referrals.item.format",
                                                 telegram_id=referral_data['telegram_id'],
                                                 total_earned=int(referral_data['total_earned']),
                                                 currency=EnvKeys.PAY_CURRENCY
                                                 ),
        item_callback=lambda referral_data: f"referral_earnings_{referral_data['telegram_id']}",
        page=0,
        per_page=10,
        back_cb="referral_system",
        nav_cb_prefix="referrals_page_"
    )

    await call.message.edit_text(
        localize("referrals.list.title"),
        reply_markup=markup
    )


# Pagination for referral list
@router.callback_query(F.data.startswith("referrals_page_"))
async def referrals_pagination_handler(call: CallbackQuery, state: FSMContext):
    """
    Pagination processing for the referral list.
    """
    try:
        page = int(call.data.split("_")[-1])
    except (ValueError, IndexError):
        await call.answer(localize("errors.pagination_invalid"))
        return

    user_id = call.from_user.id
    referrals = get_user_referrals_list(user_id)

    if not referrals:
        await call.answer(localize("referrals.list.empty"))
        return

    markup = paginated_keyboard(
        items=referrals,
        item_text=lambda referral_data: localize("referrals.item.format",
                                                 telegram_id=referral_data['telegram_id'],
                                                 total_earned=int(referral_data['total_earned']),
                                                 currency=EnvKeys.PAY_CURRENCY
                                                 ),
        item_callback=lambda referral_data: f"referral_earnings_{referral_data['telegram_id']}",
        page=page,
        per_page=10,
        back_cb="referral_system",
        nav_cb_prefix="referrals_page_"
    )

    await call.message.edit_text(
        localize("referrals.list.title"),
        reply_markup=markup
    )


# View accruals from a specific referral
@router.callback_query(F.data.startswith("referral_earnings_"))
async def referral_earnings_handler(call: CallbackQuery, state: FSMContext):
    """
    Show all accruals from a specific referral.
    """
    try:
        referral_id = int(call.data.split("_")[-1])
    except (ValueError, IndexError):
        await call.answer(localize("errors.invalid_data"))
        return

    user_id = call.from_user.id
    earnings = get_referral_earnings_from_user(user_id, referral_id)
    user_info = await call.message.bot.get_chat(referral_id)

    if not earnings:
        await call.message.edit_text(
            localize("referral.earnings.empty", id=referral_id, name=user_info.first_name),
            reply_markup=back("view_referrals")
        )
        return

    markup = paginated_keyboard(
        items=earnings,
        item_text=lambda earning: localize("referral.earning.format",
                                           amount=int(earning.amount),
                                           currency=EnvKeys.PAY_CURRENCY,
                                           date=earning.created_at.strftime("%d.%m.%Y %H:%M"),
                                           original_amount=int(earning.original_amount)
                                           ),
        item_callback=lambda earning: f"earning_detail:{earning.id}:referral_earnings_{referral_id}",
        page=0,
        per_page=10,
        back_cb="view_referrals",
        nav_cb_prefix=f"ref_earnings_{referral_id}_page_"
    )
    user_info = await call.message.bot.get_chat(referral_id)
    title_text = localize("referral.earnings.title", telegram_id=referral_id, name=user_info.first_name)
    await call.message.edit_text(title_text, reply_markup=markup)


# View all referral earnings
@router.callback_query(F.data == "view_all_earnings")
async def view_all_earnings_handler(call: CallbackQuery, state: FSMContext):
    """
    Show all user referral charges.
    """
    user_id = call.from_user.id
    earnings = get_all_referral_earnings(user_id)

    if not earnings:
        await call.message.edit_text(
            localize("all.earnings.empty"),
            reply_markup=back("referral_system")
        )
        return

    markup = paginated_keyboard(
        items=earnings,
        item_text=lambda earning: localize("all.earning.format",
                                           amount=int(earning.amount),
                                           currency=EnvKeys.PAY_CURRENCY,
                                           referral_id=earning.referral_id,
                                           date=earning.created_at.strftime("%d.%m.%Y %H:%M")
                                           ),
        item_callback=lambda earning: f"earning_detail:{earning.id}:view_all_earnings",
        page=0,
        per_page=10,
        back_cb="referral_system",
        nav_cb_prefix="all_earnings_page_"
    )

    await call.message.edit_text(
        localize("all.earnings.title"),
        reply_markup=markup
    )


# Pagination for all accruals
@router.callback_query(F.data.startswith("all_earnings_page_"))
async def all_earnings_pagination_handler(call: CallbackQuery, state: FSMContext):
    """
    Pagination processing for all referral charges.
    """
    try:
        page = int(call.data.split("_")[-1])
    except (ValueError, IndexError):
        await call.answer(localize("errors.pagination_invalid"))
        return

    user_id = call.from_user.id
    earnings = get_all_referral_earnings(user_id)

    if not earnings:
        await call.answer(localize("all.earnings.empty"))
        return

    markup = paginated_keyboard(
        items=earnings,
        item_text=lambda earning: localize("all.earning.format",
                                           amount=int(earning.amount),
                                           currency=EnvKeys.PAY_CURRENCY,
                                           referral_id=earning.referral_id,
                                           date=earning.created_at.strftime("%d.%m.%Y %H:%M")
                                           ),
        item_callback=lambda earning: f"earning_detail:{earning.id}:all_earnings_page_{page}",
        page=page,
        per_page=10,
        back_cb="referral_system",
        nav_cb_prefix="all_earnings_page_"
    )

    await call.message.edit_text(
        localize("all.earnings.title"),
        reply_markup=markup
    )


# Referral system
@router.callback_query(F.data.startswith("earning_detail:"))
async def referral_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Show referral info, personal invite link, and additional buttons.
    """
    trash, earning_id, back_data = call.data.split(':', 2)
    earning_info = get_one_referral_earning(int(earning_id))
    user_info = await call.message.bot.get_chat(earning_info['referral_id'])

    await call.message.edit_text(localize('referral.item.info',
                                          id=earning_id,
                                          telegram_id=earning_info['referral_id'],
                                          name=user_info.first_name,
                                          amount=earning_info['amount'],
                                          currency=EnvKeys.PAY_CURRENCY,
                                          date=earning_info['created_at'].strftime("%d.%m.%Y %H:%M"),
                                          original_amount=earning_info['original_amount']
                                          ), reply_markup=back(back_data))
    await state.clear()
