TRANSLATIONS: dict[str, str] = {
    # === Common Buttons ===
    "btn.shop": "🏪 Shop",
    "btn.rules": "📜 Rules",
    "btn.profile": "👤 Profile",
    "btn.support": "🆘 Support",
    "btn.channel": "ℹ News channel",
    "btn.admin_menu": "🎛 Admin panel",
    "btn.back": "⬅️ Back",
    "btn.to_menu": "🏠 Menu",
    "btn.close": "✖ Close",
    "btn.buy": "🛒 Buy",
    "btn.yes": "✅ Yes",
    "btn.no": "❌ No",
    "btn.check": "🔄 Check",
    "btn.check_subscription": "🔄 Check subscription",
    "btn.check_payment": "🔄 Check payment",
    "btn.pay": "💳 Pay",
    "btn.pay.crypto": "💎 CryptoPay",
    "btn.pay.stars": "⭐ Telegram Stars",
    "btn.pay.tg": "💸 Telegram Payments",
    # === Admin Buttons (user management shortcuts) ===
    "btn.admin.view_profile": "👁 View profile",
    "btn.admin.promote": "⬆️ Make admin",
    "btn.admin.demote": "⬇️ Remove admin",
    "btn.admin.replenish_user": "💸 Top up balance",
    # === Titles / Generic Texts ===
    "menu.title": "⛩️ Main menu",
    "profile.caption": "👤 <b>Profile</b> — {name}",
    "rules.not_set": "❌ Rules have not been added",
    # === Profile ===
    "btn.replenish": "💳 Top up your balance",
    "btn.referral": "🎲 Referral system",
    "btn.purchased": "🎁 Purchased goods",
    "profile.referral_id": "👤 <b>Referral</b> — <code>{id}</code>",
    # === Subscription Flow ===
    "subscribe.prompt": "First, subscribe to the news channel",
    "subscribe.open_channel": "Open channel",
    # === Profile Info Lines ===
    "profile.id": "🆔 <b>ID</b> — <code>{id}</code>",
    "profile.balance": "💳 <b>Balance</b> — <code>{amount}</code> {currency}",
    "profile.total_topup": "💵 <b>Total topped up</b> — <code>{amount}</code> {currency}",
    "profile.purchased_count": "🎁 <b>Purchased items</b> — {count} pcs",
    "profile.registration_date": "🕢 <b>Registered at</b> — <code>{dt}</code>",
    # === Referral ===
    "referral.title": "💚 Referral system",
    "referral.link": "🔗 Link: https://t.me/{bot_username}?start={user_id}",
    "referral.count": "Referrals count: {count}",
    "referral.description": (
        "📔 The referral system lets you earn without any investment. "
        "Share your personal link and you will receive {percent}% of your referrals’ "
        "top-ups to your bot balance."
    ),
    # === Admin: Main Menu ===
    "admin.menu.main": "⛩️ Admin Menu",
    "admin.menu.shop": "🛒 Shop management",
    "admin.menu.goods": "📦 Items management",
    "admin.menu.categories": "📂 Categories management",
    "admin.menu.users": "👥 Users management",
    "admin.menu.broadcast": "📝 Broadcast",
    "admin.menu.rights": "Insufficient permissions",
    # === Admin: User Management ===
    "admin.users.prompt_enter_id": "👤 Enter the user ID to view / edit data",
    "admin.users.invalid_id": "⚠️ Please enter a valid numeric user ID.",
    "admin.users.profile_unavailable": "❌ Profile unavailable (such user never existed)",
    "admin.users.confirm_view": "Are you sure you want to view user {id}'s profile?",
    "admin.users.not_found": "❌ User not found",
    "admin.users.cannot_change_owner": "You cannot change the owner’s role",
    "admin.users.referrals": "👥 <b>User referrals</b> — {count}",
    "admin.users.role": "🎛 <b>Role</b> — {role}",
    "admin.users.set_admin.success": "✅ Role assigned to {name}",
    "admin.users.set_admin.notify": "✅ You have been granted the ADMIN role",
    "admin.users.remove_admin.success": "✅ Admin role revoked from {name}",
    "admin.users.remove_admin.notify": "❌ Your ADMIN role has been revoked",
    "admin.users.balance.topped": "✅ {name}'s balance has been topped up by {amount} {currency}",
    "admin.users.balance.topped.notify": "✅ Your balance has been topped up by {amount} {currency}",
    # === Admin: Shop Management Menu ===
    "admin.shop.menu.title": "⛩️ Shop management",
    "admin.shop.menu.statistics": "📊 Statistics",
    "admin.shop.menu.logs": "📁 Show logs",
    "admin.shop.menu.admins": "👮 Admins",
    "admin.shop.menu.users": "👤 Users",
    "admin.shop.menu.search_bought": "🔎 Search purchased item",
    # === Admin: Categories Management ===
    "admin.categories.menu.title": "⛩️ Categories management",
    "admin.categories.add": "➕ Add category",
    "admin.categories.rename": "✏️ Rename category",
    "admin.categories.delete": "🗑 Delete category",
    "admin.categories.prompt.add": "Enter a new category name:",
    "admin.categories.prompt.delete": "Enter the category name to delete:",
    "admin.categories.prompt.rename.old": "Enter the current category name to rename:",
    "admin.categories.prompt.rename.new": "Enter the new category name:",
    "admin.categories.add.exist": "❌ Category not created (already exists)",
    "admin.categories.add.success": "✅ Category created",
    "admin.categories.delete.not_found": "❌ Category not deleted (does not exist)",
    "admin.categories.delete.success": "✅ Category deleted",
    "admin.categories.rename.not_found": "❌ Category cannot be updated (does not exist)",
    "admin.categories.rename.exist": "❌ Cannot rename (a category with this name already exists)",
    "admin.categories.rename.success": '✅ Category "{old}" renamed to "{new}"',
    # === Admin: Goods / Items Management (Add / List / Item Info) ===
    "admin.goods.add_position": "➕ add item",
    "admin.goods.add_item": "➕ Add product to item",
    "admin.goods.update_position": "📝 change item",
    "admin.goods.delete_position": "❌ delete item",
    "admin.goods.show_items": "📄 show goods in item",
    "admin.goods.add.prompt.name": "Enter the item name",
    "admin.goods.add.name.exists": "❌ Item cannot be created (it already exists)",
    "admin.goods.add.prompt.description": "Enter item description:",
    "admin.goods.add.prompt.price": "Enter item price (number in {currency}):",
    "admin.goods.add.price.invalid": "⚠️ Invalid price. Please enter a number.",
    "admin.goods.add.prompt.category": "Enter the category the item belongs to:",
    "admin.goods.add.category.not_found": "❌ Item cannot be created (invalid category provided)",
    "admin.goods.add.infinity.question": "Should this item have infinite values? (everyone will receive the same value copy)",
    "admin.goods.add.values.prompt_multi": (
        "Send product values one per message.\n"
        "When finished, press “Add the listed goods”."
    ),
    "admin.goods.add.values.added": "✅ Value “{value}” added to the list ({count} pcs).",
    "admin.goods.add.result.created": "✅ Item has been created.",
    "admin.goods.add.result.added": "📦 Added values: <b>{n}</b>",
    "admin.goods.add.result.skipped_db_dup": "↩️ Skipped (already in DB): <b>{n}</b>",
    "admin.goods.add.result.skipped_batch_dup": "🔁 Skipped (duplicate in input): <b>{n}</b>",
    "admin.goods.add.result.skipped_invalid": "🚫 Skipped (empty/invalid): <b>{n}</b>",
    "admin.goods.add.single.prompt_value": "Enter a single value for the item:",
    "admin.goods.add.single.empty": "⚠️ Value cannot be empty.",
    "admin.goods.add.single.created": "✅ Item created, value added",
    "btn.add_values_finish": "Add the listed goods",
    "admin.goods.position.not_found": "❌ No goods (this item doesn't exist)",
    "admin.goods.list_in_position.empty": "ℹ️ There are no goods in this item yet.",
    "admin.goods.list_in_position.title": "Goods in item:",
    "admin.goods.item.invalid": "Invalid data",
    "admin.goods.item.invalid_id": "Invalid item ID",
    "admin.goods.item.not_found": "Item not found",
    "admin.goods.prompt.enter_item_name": "Enter the item name",
    "admin.goods.menu.title": "⛩️ Items management menu",
    # === Admin: Goods / Items Update Flow ===
    "admin.goods.update.amount.prompt.name": "Enter the item name",
    "admin.goods.update.amount.not_exists": "❌ Unable to add values (item does not exist)",
    "admin.goods.update.amount.infinity_forbidden": "❌ Unable to add values (this item is infinite)",
    "admin.goods.update.values.result.title": "✅ Values added",
    "admin.goods.update.position.invalid": "Item not found.",
    "admin.goods.update.position.exists": "An item with this name already exists.",
    "admin.goods.update.prompt.name": "Enter the item name",
    "admin.goods.update.not_exists": "❌ Item cannot be updated (does not exist)",
    "admin.goods.update.prompt.new_name": "Enter a new item name:",
    "admin.goods.update.prompt.description": "Enter item description:",
    "admin.goods.update.infinity.make.question": "Do you want to make the item infinite?",
    "admin.goods.update.infinity.deny.question": "Do you want to disable infinity?",
    "admin.goods.update.success": "✅ Item updated",
    # === Admin: Goods / Items Delete Flow ===
    "admin.goods.delete.prompt.name": "Enter the item name",
    "admin.goods.delete.position.not_found": "❌ item not deleted (this item doesn't exist)",
    "admin.goods.delete.position.success": "✅ item deleted",
    "admin.goods.item.delete.button": "❌ Delete item",
    "admin.goods.item.already_deleted_or_missing": "Item already deleted or not found",
    "admin.goods.item.deleted": "✅ Item deleted",
    # === Admin: Item Info ===
    "admin.goods.item.info.position": "<b>Item</b>: <code>{name}</code>",
    "admin.goods.item.info.price": "<b>Price</b>: <code>{price}</code> {currency}",
    "admin.goods.item.info.id": "<b>Unique ID</b>: <code>{id}</code>",
    "admin.goods.item.info.value": "<b>Product</b>: <code>{value}</code>",
    # === Admin: Logs ===
    "admin.shop.logs.caption": "Bot logs",
    "admin.shop.logs.empty": "❗️ No logs yet",
    # === Group Notifications ===
    "shop.group.new_upload": "New stock",
    "shop.group.item": "Item",
    "shop.group.count": "Quantity",
    # === Admin: Statistics ===
    "admin.shop.stats.template": (
        "Shop statistics:\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "<b>◽USERS</b>\n"
        "◾️Users in last 24h: {today_users}\n"
        "◾️Total admins: {admins}\n"
        "◾️Total users: {users}\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "◽<b>FUNDS</b>\n"
        "◾Sales in last 24h: {today_orders} {currency}\n"
        "◾Total sold: {all_orders} {currency}\n"
        "◾Top-ups in last 24h: {today_topups} {currency}\n"
        "◾Funds in system: {system_balance} {currency}\n"
        "◾Total top-ups: {all_topups} {currency}\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "◽<b>MISC</b>\n"
        "◾Items: {items} pcs\n"
        "◾Positions: {goods} pcs\n"
        "◾Categories: {categories} pcs\n"
        "◾Sold items: {sold_count} pcs"
    ),
    # === Admin: Lists & Broadcast ===
    "admin.shop.admins.title": "👮 Bot admins:",
    "admin.shop.users.title": "Bot users:",
    "admin.shop.bought.prompt_id": "Enter purchased item unique ID",
    "admin.shop.bought.not_found": "❌ Item with given unique ID not found",
    "broadcast.prompt": "Send a message to broadcast:",
    "broadcast.done": "Broadcast finished. Message sent to {count} users.",
    # === Payments / Top-up Flow ===
    "payments.replenish_prompt": "Enter top-up amount in {currency}:",
    "payments.replenish_invalid": "❌ Invalid amount. Enter a number from {min_amount} to {max_amount} {currency}.",
    "payments.method_choose": "Choose a payment method:",
    "payments.not_configured": "❌ Top-ups are not configured",
    "payments.session_expired": "Payment session has expired. Please start again.",
    "payments.crypto.create_fail": "❌ Failed to create invoice: {error}",
    "payments.stars.create_fail": "❌ Failed to issue Stars invoice: {error}",
    "payments.fiat.create_fail": "❌ Failed to issue invoice: {error}",
    "payments.no_active_invoice": "❌ No active invoices found. Start top-up again.",
    "payments.invoice_not_found": "❌ Invoice not found. Please start again.",
    "payments.not_paid_yet": "⌛️ Payment is not completed yet.",
    "payments.expired": "❌ Invoice has expired.",
    "payments.invoice.summary": (
        "💵 Top-up amount: {amount} {currency}.\n"
        "⌛️ You have {minutes} minutes to pay.\n"
        "<b>❗️ After paying, press «{button}»</b>"
    ),
    "payments.unable_determine_amount": "❌ Failed to determine the paid amount.",
    "payments.topped_simple": "✅ Balance topped up by {amount} {currency}",
    "payments.topped_with_suffix": "✅ Balance topped up by {amount} {currency} ({suffix})",
    "payments.success_suffix.stars": "Telegram Stars",
    "payments.success_suffix.tg": "Telegram Payments",
    "payments.referral.bonus": "✅ You received {amount} {currency} from your referral {name}",
    "payments.invoice.title.topup": "Balance top-up",
    "payments.invoice.desc.topup.stars": "Top-up {amount} {currency} via Telegram Stars",
    "payments.invoice.desc.topup.fiat": "Pay via Telegram Payments (card)",
    "payments.invoice.label.fiat": "Top-up {amount} {currency}",
    "payments.invoice.label.stars": "{stars} ⭐️",
    # === Shop Browsing (Categories / Goods / Item Page) ===
    "shop.categories.title": "🏪 Shop categories",
    "shop.goods.choose": "🏪 Choose a product",
    "shop.item.not_found": "Item not found",
    "shop.item.title": "🏪 Item {name}",
    "shop.item.description": "Description: {description}",
    "shop.item.price": "Price — {amount} {currency}",
    "shop.item.quantity_unlimited": "Quantity — unlimited",
    "shop.item.quantity_left": "Quantity — {count} pcs",
    "shop.insufficient_funds": "❌ Insufficient funds",
    "shop.out_of_stock": "❌ Item is out of stock",
    "shop.purchase.success": "✅ Item purchased. <b>Balance</b>: <i>{balance}</i> {currency}\n\n{value}",
    # === Purchases ===
    "purchases.title": "Purchased items:",
    "purchases.pagination.invalid": "Invalid pagination data",
    "purchases.item.not_found": "Purchase not found",
    "purchases.item.name": "<b>🧾 Item</b>: <code>{name}</code>",
    "purchases.item.price": "<b>💵 Price</b>: <code>{amount}</code> {currency}",
    "purchases.item.datetime": "<b>🕒 Purchased at</b>: <code>{dt}</code>",
    "purchases.item.unique_id": "<b>🧾 Unique ID</b>: <code>{uid}</code>",
    "purchases.item.value": "<b>🔑 Value</b>:\n<code>{value}</code>",
    "purchases.item.buyer": "<b>Buyer</b>: <code>{buyer}</code>",
    # === Errors ===
    "errors.not_subscribed": "You are not subscribed",
    "errors.something_wrong": "❌ Something went wrong. Please try again.",
    "errors.pagination_invalid": "Invalid pagination data",
    "errors.invalid_data": "❌ Invalid data",
    "errors.id_should_be_number": "❌ ID must be a number.",
}
