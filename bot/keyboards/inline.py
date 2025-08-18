from typing import Callable, Iterable, Tuple
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.i18n import localize


def main_menu(role: int, channel: str | None = None, helper: str | None = None) -> InlineKeyboardMarkup:
    """
    Main menu.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text=localize("btn.shop"), callback_data="shop")
    kb.button(text=localize("btn.rules"), callback_data="rules")
    kb.button(text=localize("btn.profile"), callback_data="profile")
    if helper:
        kb.button(text=localize("btn.support"), url=f"https://t.me/{helper.lstrip('@')}")
    if channel:
        kb.button(text=localize("btn.channel"), url=f"https://t.me/{channel.lstrip('@')}")
    if role > 1:
        kb.button(text=localize("btn.admin_menu"), callback_data="console")
    kb.adjust(2)
    return kb.as_markup()


def profile_keyboard(referral_percent: int, user_items: int = 0) -> InlineKeyboardMarkup:
    """
    Profile keyboard.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text=localize("btn.replenish"), callback_data="replenish_balance")
    if referral_percent != 0:
        kb.button(text=localize("btn.referral"), callback_data="referral_system")
    if user_items != 0:
        kb.button(text=localize("btn.purchased"), callback_data="bought_items")
    kb.button(text=localize("btn.back"), callback_data="back_to_menu")
    kb.adjust(1)
    return kb.as_markup()


def admin_console_keyboard() -> InlineKeyboardMarkup:
    """
    Admin panel.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text=localize("admin.menu.shop"), callback_data="shop_management")
    kb.button(text=localize("admin.menu.goods"), callback_data="goods_management")
    kb.button(text=localize("admin.menu.categories"), callback_data="categories_management")
    kb.button(text=localize("admin.menu.users"), callback_data="user_management")
    kb.button(text=localize("admin.menu.broadcast"), callback_data="send_message")
    kb.button(text=localize("btn.back"), callback_data="back_to_menu")
    kb.adjust(1)
    return kb.as_markup()


def simple_buttons(buttons: Iterable[Tuple[str, str]], per_row: int = 1) -> InlineKeyboardMarkup:
    """
    Universal button assembly from (text, callback_data)
    """
    kb = InlineKeyboardBuilder()
    for text, cb in buttons:
        kb.button(text=text, callback_data=cb)
    kb.adjust(per_row)
    return kb.as_markup()


def back(cb: str = "menu", text: str | None = None) -> InlineKeyboardMarkup:
    """
    One 'Back' button.
    """
    return simple_buttons([(text or localize("btn.back"), cb)])


def close() -> InlineKeyboardMarkup:
    """
    One button 'Close'.
    """
    return simple_buttons([(localize("btn.close"), "close")])


def paginated_keyboard(
        items: list,
        item_text: Callable[[object], str],
        item_callback: Callable[[object], str],
        page: int = 0,
        per_page: int = 10,
        back_cb: str | None = None,
        nav_cb_prefix: str = "",
        back_text: str | None = None,
) -> InlineKeyboardMarkup:
    """
    Pagination: 1 item per row, navigation below, 'Back' below.
    """
    kb = InlineKeyboardBuilder()
    total = len(items)
    start = page * per_page
    end = start + per_page

    for item in items[start:end]:
        kb.button(text=item_text(item), callback_data=item_callback(item))
    kb.adjust(1)

    # расчёт страниц
    max_page = max((total - 1) // per_page, 0)
    if max_page > 0:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"{nav_cb_prefix}{page - 1}"))
        nav_buttons.append(InlineKeyboardButton(text=f"{page + 1}/{max_page + 1}", callback_data="noop"))
        if page < max_page:
            nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"{nav_cb_prefix}{page + 1}"))
        kb.row(*nav_buttons)

    if back_cb:
        kb.row(InlineKeyboardButton(text=back_text or localize("btn.back"), callback_data=back_cb))

    return kb.as_markup()


def item_info(item_name: str, category: str) -> InlineKeyboardMarkup:
    """
    Product card.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text=localize("btn.buy"), callback_data=f"buy_{item_name}")
    kb.button(text=localize("btn.back"), callback_data=f"category_{category}")
    kb.adjust(2)
    return kb.as_markup()


def payment_menu(pay_url: str) -> InlineKeyboardMarkup:
    """
    Buttons under the invoice (CryptoPay, etc.).
    """
    kb = InlineKeyboardBuilder()
    kb.button(text=localize("btn.pay"), url=pay_url)
    kb.button(text=localize("btn.check_payment"), callback_data="check")
    kb.button(text=localize("btn.back"), callback_data="profile")
    kb.adjust(1)
    return kb.as_markup()


def get_payment_choice() -> InlineKeyboardMarkup:
    """
    Select a payment method.
    """
    return simple_buttons(
        [
            (localize("btn.pay.crypto"), "pay_cryptopay"),
            (localize("btn.pay.stars"), "pay_stars"),
            (localize("btn.pay.tg"), "pay_fiat"),
            (localize("btn.back"), "replenish_balance"),
        ],
        per_row=1,
    )


def question_buttons(question: str, back_data: str) -> InlineKeyboardMarkup:
    """
    Universal yes/no + Back.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text=localize("btn.yes"), callback_data=f"{question}_yes")
    kb.button(text=localize("btn.no"), callback_data=f"{question}_no")
    kb.button(text=localize("btn.back"), callback_data=back_data)
    kb.adjust(2)
    return kb.as_markup()
