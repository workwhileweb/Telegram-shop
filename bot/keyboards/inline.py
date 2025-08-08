from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu(role: int, channel: str = None, helper: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏪 Магазин", callback_data="shop")
    kb.button(text="📜 Правила", callback_data="rules")
    kb.button(text="👤 Профиль", callback_data="profile")
    if helper:
        kb.button(text="🆘 Поддержка", url=f"https://t.me/{helper.lstrip('@')}")
    if channel:
        kb.button(text="ℹ Новостной канал", url=f"https://t.me/{channel.lstrip('@')}")
    if role > 1:
        kb.button(text="🎛 Панель администратора", callback_data="console")
    kb.adjust(2)
    return kb.as_markup()


def profile_keyboard(referral_percent: int, user_items: int = 0) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Пополнить баланс", callback_data="replenish_balance")
    if referral_percent != 0:
        kb.button(text="🎲 Реферальная система", callback_data="referral_system")
    if user_items != 0:
        kb.button(text="🎁 Купленные товары", callback_data="bought_items")
    kb.button(text="🔙 Вернуться назад", callback_data="back_to_menu")
    kb.adjust(1)
    return kb.as_markup()


def admin_console_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Управление магазином", callback_data="shop_management")
    kb.button(text="📦 Управление позициями", callback_data="goods_management")
    kb.button(text="📂 Управление категориями", callback_data="categories_management")
    kb.button(text="👥 Управление пользователями", callback_data="user_management")
    kb.button(text="📝 Рассылка", callback_data="send_message")
    kb.button(text="🔙 Вернуться назад", callback_data="back_to_menu")
    kb.adjust(1)
    return kb.as_markup()


def simple_buttons(buttons: list[tuple[str, str]], per_row=1) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for text, cb in buttons:
        kb.button(text=text, callback_data=cb)
    kb.adjust(per_row)
    return kb.as_markup()


def back(cb: str = "menu", text: str = "🔙 Вернуться назад") -> InlineKeyboardMarkup:
    return simple_buttons([(text, cb)])


def close() -> InlineKeyboardMarkup:
    return simple_buttons([("✖ Закрыть", "close")])


def paginated_keyboard(
        items: list,
        item_text: callable,
        item_callback: callable,
        page: int = 0,
        per_page: int = 10,
        back_cb: str = None,
        nav_cb_prefix: str = "",
        back_text: str = "🔙 Вернуться назад"
) -> InlineKeyboardMarkup:
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
        nav_buttons.append(InlineKeyboardButton(text=f"{page + 1}/{max_page + 1}", callback_data="dummy_button"))
        if page < max_page:
            nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"{nav_cb_prefix}{page + 1}"))
        kb.row(*nav_buttons)

    if back_cb:
        kb.row(InlineKeyboardButton(text=back_text, callback_data=back_cb))

    return kb.as_markup()


def item_info(item_name: str, category: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Купить", callback_data=f"buy_{item_name}")
    kb.button(text="🔙 Вернуться назад", callback_data=f"category_{category}")
    kb.adjust(2)
    return kb.as_markup()


def payment_menu(pay_url: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Оплатить", url=pay_url)
    kb.button(text="🔄 Проверить оплату", callback_data="check")
    kb.button(text="🔙 Вернуться назад", callback_data="profile")
    kb.adjust(1)
    return kb.as_markup()


def get_payment_choice() -> InlineKeyboardMarkup:
    return simple_buttons([
        ("💸 YooMoney", "pay_yoomoney"),
        ("💎 CryptoPay", "pay_cryptopay"),
        ("🔙 Вернуться назад", "replenish_balance")
    ], per_row=1)


def question_buttons(question: str, back_data: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да", callback_data=f"{question}_yes")
    kb.button(text="❌ Нет", callback_data=f"{question}_no")
    kb.button(text="🔙 Вернуться назад", callback_data=back_data)
    kb.adjust(2)
    return kb.as_markup()
