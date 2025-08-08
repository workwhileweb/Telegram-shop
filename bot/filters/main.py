from dataclasses import dataclass

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from bot.database.methods import check_role


@dataclass
class ValidAmountFilter(BaseFilter):
    """
    Валидация суммы пополнения (используемся в FSM шагах).
    """
    min_amount: int = 20
    max_amount: int = 10_000

    async def __call__(self, message: Message) -> bool:
        text: str = message.text or ""
        if not text.isdigit():
            return False
        value = int(text)
        return self.min_amount <= value <= self.max_amount


@dataclass
class HasPermissionFilter(BaseFilter):
    """
    Фильтр на наличие определённого permission у пользователя (битовая маска).
    """
    permission: int

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        # check_role(user_id) возвращает int (битовая маска прав) или None
        user_permissions: int = check_role(user_id) or 0
        return (user_permissions & self.permission) == self.permission
