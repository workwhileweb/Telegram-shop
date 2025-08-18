from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.i18n import localize
from bot.keyboards import admin_console_keyboard
from bot.database.methods import check_role
from bot.filters import HasPermissionFilter
from bot.database.models import Permission

# Importing child routers
from bot.handlers.admin.broadcast import router as broadcast_router
from bot.handlers.admin.shop_management_states import router as shop_management_router
from bot.handlers.admin.user_management_states import router as user_management_router
from bot.handlers.admin.categories_management_states import router as categories_management_router
from bot.handlers.admin.goods_management_states import router as goods_management_router
from bot.handlers.admin.adding_position_states import router as add_management_router
from bot.handlers.admin.update_position_states import router as update_management_router

router = Router()


# Admin menu - for admins only (SHOP_MANAGE)
@router.callback_query(F.data == 'console', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def console_callback_handler(call: CallbackQuery):
    """
    Admin menu (only for admins and above).
    """
    user_id = call.from_user.id
    role = check_role(user_id)
    if role > 1:
        await call.message.edit_text(localize("admin.menu.main"), reply_markup=admin_console_keyboard())
    else:
        await call.answer(localize("admin.menu.rights"))


# Connect all nested routers
router.include_router(broadcast_router)
router.include_router(shop_management_router)
router.include_router(user_management_router)
router.include_router(categories_management_router)
router.include_router(goods_management_router)
router.include_router(add_management_router)
router.include_router(update_management_router)
