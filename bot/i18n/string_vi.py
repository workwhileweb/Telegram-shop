TRANSLATIONS: dict[str, str] = {
    # === Common Buttons ===
    "btn.shop": "🏪 Cửa hàng",
    "btn.rules": "📜 Quy tắc",
    "btn.profile": "👤 Hồ sơ",
    "btn.support": "🆘 Hỗ trợ",
    "btn.channel": "ℹ Kênh tin tức",
    "btn.admin_menu": "🎛 Bảng quản trị",
    "btn.back": "⬅️ Quay lại",
    "btn.to_menu": "🏠 Menu",
    "btn.close": "✖ Đóng",
    "btn.buy": "🛒 Mua",
    "btn.yes": "✅ Có",
    "btn.no": "❌ Không",
    "btn.check": "🔄 Kiểm tra",
    "btn.check_subscription": "🔄 Kiểm tra đăng ký",
    "btn.check_payment": "🔄 Kiểm tra thanh toán",
    "btn.pay": "💳 Thanh toán",
    "btn.pay.crypto": "💎 CryptoPay",
    "btn.pay.stars": "⭐ Telegram Stars",
    "btn.pay.tg": "💸 Telegram Payments",
    # === Admin Buttons (user management shortcuts) ===
    "btn.admin.view_profile": "👁 Xem hồ sơ",
    "btn.admin.promote": "⬆️ Thăng làm admin",
    "btn.admin.demote": "⬇️ Gỡ bỏ admin",
    "btn.admin.replenish_user": "💸 Nạp tiền",
    # === Titles / Generic Texts ===
    "menu.title": "⛩️ Menu chính",
    "profile.caption": "👤 <b>Hồ sơ</b> — {name}",
    "rules.not_set": "❌ Chưa có quy tắc nào được thêm",
    # === Profile ===
    "btn.replenish": "💳 Nạp tiền vào tài khoản",
    "btn.referral": "🎲 Hệ thống giới thiệu",
    "btn.purchased": "🎁 Hàng đã mua",
    "profile.referral_id": "👤 <b>Giới thiệu</b> — <code>{id}</code>",
    # === Subscription Flow ===
    "subscribe.prompt": "Trước tiên, hãy đăng ký kênh tin tức",
    "subscribe.open_channel": "Mở kênh",
    # === Profile Info Lines ===
    "profile.id": "🆔 <b>ID</b> — <code>{id}</code>",
    "profile.balance": "💳 <b>Số dư</b> — <code>{amount}</code> {currency}",
    "profile.total_topup": "💵 <b>Tổng nạp tiền</b> — <code>{amount}</code> {currency}",
    "profile.purchased_count": "🎁 <b>Số mặt hàng đã mua</b> — {count} cái",
    "profile.registration_date": "🕢 <b>Đăng ký lúc</b> — <code>{dt}</code>",
    # === Referral ===
    "referral.title": "💚 Hệ thống giới thiệu",
    "referral.link": "🔗 Liên kết: https://t.me/{bot_username}?start={user_id}",
    "referral.count": "Số người giới thiệu: {count}",
    "referral.description": (
        "📔 Hệ thống giới thiệu cho phép bạn kiếm tiền mà không cần đầu tư. "
        "Chia sẻ liên kết cá nhân của bạn và bạn sẽ nhận được {percent}% từ "
        "các khoản nạp tiền của người được giới thiệu vào số dư bot của bạn."
    ),
    # === Admin: Main Menu ===
    "admin.menu.main": "⛩️ Menu quản trị",
    "admin.menu.shop": "🛒 Quản lý cửa hàng",
    "admin.menu.goods": "📦 Quản lý mặt hàng",
    "admin.menu.categories": "📂 Quản lý danh mục",
    "admin.menu.users": "👥 Quản lý người dùng",
    "admin.menu.broadcast": "📝 Gửi thông báo",
    "admin.menu.rights": "Không đủ quyền hạn",
    # === Admin: User Management ===
    "admin.users.prompt_enter_id": "👤 Nhập ID người dùng để xem / chỉnh sửa dữ liệu",
    "admin.users.invalid_id": "⚠️ Vui lòng nhập ID người dùng hợp lệ.",
    "admin.users.profile_unavailable": "❌ Không thể xem hồ sơ (người dùng này chưa bao giờ tồn tại)",
    "admin.users.confirm_view": "Bạn có chắc chắn muốn xem hồ sơ của người dùng {id}?",
    "admin.users.not_found": "❌ Không tìm thấy người dùng",
    "admin.users.cannot_change_owner": "Bạn không thể thay đổi vai trò của chủ sở hữu",
    "admin.users.referrals": "👥 <b>Người được giới thiệu</b> — {count}",
    "admin.users.role": "🎛 <b>Vai trò</b> — {role}",
    "admin.users.set_admin.success": "✅ Đã gán vai trò cho {name}",
    "admin.users.set_admin.notify": "✅ Bạn đã được cấp vai trò ADMIN",
    "admin.users.remove_admin.success": "✅ Đã thu hồi vai trò admin từ {name}",
    "admin.users.remove_admin.notify": "❌ Vai trò ADMIN của bạn đã bị thu hồi",
    "admin.users.balance.topped": "✅ Số dư của {name} đã được nạp thêm {amount} {currency}",
    "admin.users.balance.topped.notify": "✅ Số dư của bạn đã được nạp thêm {amount} {currency}",
    # === Admin: Shop Management Menu ===
    "admin.shop.menu.title": "⛩️ Quản lý cửa hàng",
    "admin.shop.menu.statistics": "📊 Thống kê",
    "admin.shop.menu.logs": "📁 Hiển thị nhật ký",
    "admin.shop.menu.admins": "👮 Quản trị viên",
    "admin.shop.menu.users": "👤 Người dùng",
    "admin.shop.menu.search_bought": "🔎 Tìm kiếm mặt hàng đã mua",
    # === Admin: Categories Management ===
    "admin.categories.menu.title": "⛩️ Quản lý danh mục",
    "admin.categories.add": "➕ Thêm danh mục",
    "admin.categories.rename": "✏️ Đổi tên danh mục",
    "admin.categories.delete": "🗑 Xóa danh mục",
    "admin.categories.prompt.add": "Nhập tên danh mục mới:",
    "admin.categories.prompt.delete": "Nhập tên danh mục cần xóa:",
    "admin.categories.prompt.rename.old": "Nhập tên danh mục hiện tại cần đổi tên:",
    "admin.categories.prompt.rename.new": "Nhập tên danh mục mới:",
    "admin.categories.add.exist": "❌ Không tạo được danh mục (đã tồn tại)",
    "admin.categories.add.success": "✅ Đã tạo danh mục",
    "admin.categories.delete.not_found": "❌ Không xóa được danh mục (không tồn tại)",
    "admin.categories.delete.success": "✅ Đã xóa danh mục",
    "admin.categories.rename.not_found": "❌ Không thể cập nhật danh mục (không tồn tại)",
    "admin.categories.rename.exist": "❌ Không thể đổi tên (đã có danh mục với tên này)",
    "admin.categories.rename.success": '✅ Danh mục "{old}" đã được đổi tên thành "{new}"',
    # === Admin: Goods / Items Management (Add / List / Item Info) ===
    "admin.goods.add_position": "➕ Thêm mặt hàng",
    "admin.goods.add_item": "➕ Thêm sản phẩm vào mặt hàng",
    "admin.goods.update_position": "📝 Chỉnh sửa mặt hàng",
    "admin.goods.delete_position": "❌ Xóa mặt hàng",
    "admin.goods.show_items": "📄 Hiển thị hàng hóa trong mặt hàng",
    "admin.goods.add.prompt.name": "Nhập tên mặt hàng",
    "admin.goods.add.name.exists": "❌ Không thể tạo mặt hàng (đã tồn tại)",
    "admin.goods.add.prompt.description": "Nhập mô tả mặt hàng:",
    "admin.goods.add.prompt.price": "Nhập giá mặt hàng (số tiền bằng {currency}):",
    "admin.goods.add.price.invalid": "⚠️ Giá không hợp lệ. Vui lòng nhập một số.",
    "admin.goods.add.prompt.category": "Nhập danh mục mà mặt hàng thuộc về:",
    "admin.goods.add.category.not_found": "❌ Không thể tạo mặt hàng (danh mục không hợp lệ)",
    "admin.goods.add.infinity.question": "Mặt hàng này có nên có giá trị vô hạn không? (mọi người sẽ nhận được cùng một bản sao giá trị)",
    "admin.goods.add.values.prompt_multi": (
        "Gửi giá trị sản phẩm từng cái một.\n"
        "Khi hoàn thành, nhấn \"Thêm hàng hóa đã liệt kê\"."
    ),
    "admin.goods.add.values.added": "✅ Giá trị \"{value}\" đã được thêm vào danh sách ({count} cái).",
    "admin.goods.add.result.created": "✅ Mặt hàng đã được tạo.",
    "admin.goods.add.result.added": "📦 Giá trị đã thêm: <b>{n}</b>",
    "admin.goods.add.result.skipped_db_dup": "↩️ Đã bỏ qua (đã có trong DB): <b>{n}</b>",
    "admin.goods.add.result.skipped_batch_dup": "🔁 Đã bỏ qua (trùng lặp trong đầu vào): <b>{n}</b>",
    "admin.goods.add.result.skipped_invalid": "🚫 Đã bỏ qua (trống/không hợp lệ): <b>{n}</b>",
    "admin.goods.add.single.prompt_value": "Nhập một giá trị duy nhất cho mặt hàng:",
    "admin.goods.add.single.empty": "⚠️ Giá trị không thể để trống.",
    "admin.goods.add.single.created": "✅ Mặt hàng đã được tạo, giá trị đã được thêm",
    "btn.add_values_finish": "Thêm hàng hóa đã liệt kê",
    "admin.goods.position.not_found": "❌ Không có hàng hóa (mặt hàng này không tồn tại)",
    "admin.goods.list_in_position.empty": "ℹ️ Chưa có hàng hóa nào trong mặt hàng này.",
    "admin.goods.list_in_position.title": "Hàng hóa trong mặt hàng:",
    "admin.goods.item.invalid": "Dữ liệu không hợp lệ",
    "admin.goods.item.invalid_id": "ID mặt hàng không hợp lệ",
    "admin.goods.item.not_found": "Không tìm thấy mặt hàng",
    "admin.goods.prompt.enter_item_name": "Nhập tên mặt hàng",
    "admin.goods.menu.title": "⛩️ Menu quản lý mặt hàng",
    # === Admin: Goods / Items Update Flow ===
    "admin.goods.update.amount.prompt.name": "Nhập tên mặt hàng",
    "admin.goods.update.amount.not_exists": "❌ Không thể thêm giá trị (mặt hàng không tồn tại)",
    "admin.goods.update.amount.infinity_forbidden": "❌ Không thể thêm giá trị (mặt hàng này là vô hạn)",
    "admin.goods.update.values.result.title": "✅ Đã thêm giá trị",
    "admin.goods.update.position.invalid": "Không tìm thấy mặt hàng.",
    "admin.goods.update.position.exists": "Đã có mặt hàng với tên này.",
    "admin.goods.update.prompt.name": "Nhập tên mặt hàng",
    "admin.goods.update.not_exists": "❌ Không thể cập nhật mặt hàng (không tồn tại)",
    "admin.goods.update.prompt.new_name": "Nhập tên mặt hàng mới:",
    "admin.goods.update.prompt.description": "Nhập mô tả mặt hàng:",
    "admin.goods.update.infinity.make.question": "Bạn có muốn làm cho mặt hàng vô hạn không?",
    "admin.goods.update.infinity.deny.question": "Bạn có muốn tắt tính năng vô hạn không?",
    "admin.goods.update.success": "✅ Đã cập nhật mặt hàng",
    # === Admin: Goods / Items Delete Flow ===
    "admin.goods.delete.prompt.name": "Nhập tên mặt hàng",
    "admin.goods.delete.position.not_found": "❌ Không xóa được mặt hàng (mặt hàng này không tồn tại)",
    "admin.goods.delete.position.success": "✅ Đã xóa mặt hàng",
    "admin.goods.item.delete.button": "❌ Xóa mặt hàng",
    "admin.goods.item.already_deleted_or_missing": "Mặt hàng đã bị xóa hoặc không tìm thấy",
    "admin.goods.item.deleted": "✅ Đã xóa mặt hàng",
    # === Admin: Item Info ===
    "admin.goods.item.info.position": "<b>Mặt hàng</b>: <code>{name}</code>",
    "admin.goods.item.info.price": "<b>Giá</b>: <code>{price}</code> {currency}",
    "admin.goods.item.info.id": "<b>ID duy nhất</b>: <code>{id}</code>",
    "admin.goods.item.info.value": "<b>Sản phẩm</b>: <code>{value}</code>",
    # === Admin: Logs ===
    "admin.shop.logs.caption": "Nhật ký bot",
    "admin.shop.logs.empty": "❗️ Chưa có nhật ký nào",
    # === Group Notifications ===
    "shop.group.new_upload": "Hàng mới",
    "shop.group.item": "Mặt hàng",
    "shop.group.count": "Số lượng",
    # === Admin: Statistics ===
    "admin.shop.stats.template": (
        "Thống kê cửa hàng:\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "<b>◽NGƯỜI DÙNG</b>\n"
        "◾️Người dùng trong 24h qua: {today_users}\n"
        "◾️Tổng số admin: {admins}\n"
        "◾️Tổng số người dùng: {users}\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "◽<b>TIỀN BẠC</b>\n"
        "◾Doanh số 24h qua: {today_orders} {currency}\n"
        "◾Tổng doanh số: {all_orders} {currency}\n"
        "◾Nạp tiền 24h qua: {today_topups} {currency}\n"
        "◾Tiền trong hệ thống: {system_balance} {currency}\n"
        "◾Tổng nạp tiền: {all_topups} {currency}\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "◽<b>KHÁC</b>\n"
        "◾Mặt hàng: {items} cái\n"
        "◾Vị trí: {goods} cái\n"
        "◾Danh mục: {categories} cái\n"
        "◾Mặt hàng đã bán: {sold_count} cái"
    ),
    # === Admin: Lists & Broadcast ===
    "admin.shop.admins.title": "👮 Quản trị viên bot:",
    "admin.shop.users.title": "Người dùng bot:",
    "admin.shop.bought.prompt_id": "Nhập ID duy nhất của mặt hàng đã mua",
    "admin.shop.bought.not_found": "❌ Không tìm thấy mặt hàng với ID duy nhất đã cho",
    "broadcast.prompt": "Gửi tin nhắn để phát sóng:",
    "broadcast.done": "Phát sóng hoàn tất. Tin nhắn đã được gửi đến {count} người dùng.",
    # === Payments / Top-up Flow ===
    "payments.replenish_prompt": "Nhập số tiền nạp bằng {currency}:",
    "payments.replenish_invalid": "❌ Số tiền không hợp lệ. Nhập số từ {min_amount} đến {max_amount} {currency}.",
    "payments.method_choose": "Chọn phương thức thanh toán:",
    "payments.not_configured": "❌ Nạp tiền chưa được cấu hình",
    "payments.session_expired": "Phiên thanh toán đã hết hạn. Vui lòng bắt đầu lại.",
    "payments.crypto.create_fail": "❌ Không thể tạo hóa đơn: {error}",
    "payments.stars.create_fail": "❌ Không thể tạo hóa đơn Stars: {error}",
    "payments.fiat.create_fail": "❌ Không thể tạo hóa đơn: {error}",
    "payments.no_active_invoice": "❌ Không tìm thấy hóa đơn đang hoạt động. Bắt đầu nạp tiền lại.",
    "payments.invoice_not_found": "❌ Không tìm thấy hóa đơn. Vui lòng bắt đầu lại.",
    "payments.not_paid_yet": "⌛️ Thanh toán chưa hoàn tất.",
    "payments.expired": "❌ Hóa đơn đã hết hạn.",
    "payments.invoice.summary": (
        "💵 Số tiền nạp: {amount} {currency}.\n"
        "⌛️ Bạn có {minutes} phút để thanh toán.\n"
        "<b>❗️ Sau khi thanh toán, nhấn «{button}»</b>"
    ),
    "payments.unable_determine_amount": "❌ Không thể xác định số tiền đã thanh toán.",
    "payments.topped_simple": "✅ Đã nạp {amount} {currency} vào số dư",
    "payments.topped_with_suffix": "✅ Đã nạp {amount} {currency} vào số dư ({suffix})",
    "payments.success_suffix.stars": "Telegram Stars",
    "payments.success_suffix.tg": "Telegram Payments",
    "payments.referral.bonus": "✅ Bạn đã nhận {amount} {currency} từ người giới thiệu {name}",
    "payments.invoice.title.topup": "Nạp tiền",
    "payments.invoice.desc.topup.stars": "Nạp {amount} {currency} qua Telegram Stars",
    "payments.invoice.desc.topup.fiat": "Thanh toán qua Telegram Payments (thẻ)",
    "payments.invoice.label.fiat": "Nạp {amount} {currency}",
    "payments.invoice.label.stars": "{stars} ⭐️",
    # === Shop Browsing (Categories / Goods / Item Page) ===
    "shop.categories.title": "🏪 Danh mục cửa hàng",
    "shop.goods.choose": "🏪 Chọn sản phẩm",
    "shop.item.not_found": "Không tìm thấy mặt hàng",
    "shop.item.title": "🏪 Mặt hàng {name}",
    "shop.item.description": "Mô tả: {description}",
    "shop.item.price": "Giá — {amount} {currency}",
    "shop.item.quantity_unlimited": "Số lượng — không giới hạn",
    "shop.item.quantity_left": "Số lượng — {count} cái",
    "shop.insufficient_funds": "❌ Không đủ tiền",
    "shop.out_of_stock": "❌ Hết hàng",
    "shop.purchase.success": "✅ Đã mua mặt hàng. <b>Số dư</b>: <i>{balance}</i> {currency}\n\n{value}",
    # === Purchases ===
    "purchases.title": "Mặt hàng đã mua:",
    "purchases.pagination.invalid": "Dữ liệu phân trang không hợp lệ",
    "purchases.item.not_found": "Không tìm thấy giao dịch mua",
    "purchases.item.name": "<b>🧾 Mặt hàng</b>: <code>{name}</code>",
    "purchases.item.price": "<b>💵 Giá</b>: <code>{amount}</code> {currency}",
    "purchases.item.datetime": "<b>🕒 Mua lúc</b>: <code>{dt}</code>",
    "purchases.item.unique_id": "<b>🧾 ID duy nhất</b>: <code>{uid}</code>",
    "purchases.item.value": "<b>🔑 Giá trị</b>:\n<code>{value}</code>",
    "purchases.item.buyer": "<b>Người mua</b>: <code>{buyer}</code>",
    # === Errors ===
    "errors.not_subscribed": "Bạn chưa đăng ký",
    "errors.something_wrong": "❌ Đã xảy ra lỗi. Vui lòng thử lại.",
    "errors.pagination_invalid": "Dữ liệu phân trang không hợp lệ",
    "errors.invalid_data": "❌ Dữ liệu không hợp lệ",
    "errors.id_should_be_number": "❌ ID phải là số.",
}
