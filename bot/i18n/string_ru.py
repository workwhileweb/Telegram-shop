TRANSLATIONS : dict[str, str] = {
# === Common Buttons ===
        "btn.shop": "🏪 Магазин",
        "btn.rules": "📜 Правила",
        "btn.profile": "👤 Профиль",
        "btn.support": "🆘 Поддержка",
        "btn.channel": "ℹ Новостной канал",
        "btn.admin_menu": "🎛 Панель администратора",
        "btn.back": "⬅️ Назад",
        "btn.to_menu": "🏠 В меню",
        "btn.close": "✖ Закрыть",
        "btn.buy": "🛒 Купить",
        "btn.yes": "✅ Да",
        "btn.no": "❌ Нет",
        "btn.check": "🔄 Проверить",
        "btn.check_subscription": "🔄 Проверить подписку",
        "btn.pay": "💳 Оплатить",
        "btn.check_payment": "🔄 Проверить оплату",
        "btn.pay.crypto": "💎 CryptoPay",
        "btn.pay.stars": "⭐ Telegram Stars",
        "btn.pay.tg": "💸 Telegram Payments",

        # === Admin Buttons (user management shortcuts) ===
        "btn.admin.view_profile": "👁 Посмотреть профиль",
        "btn.admin.promote": "⬆️ Назначить администратором",
        "btn.admin.demote": "⬇️ Снять администратора",
        "btn.admin.replenish_user": "💸 Пополнить баланс",

        # === Titles / Generic Texts ===
        "menu.title": "⛩️ Основное меню",
        "profile.caption": "👤 <b>Профиль</b> — {name}",
        "rules.not_set": "❌ Правила не были добавлены",

        # === Subscription Flow ===
        "subscribe.prompt": "Для начала подпишитесь на новостной канал",
        "subscribe.open_channel": "Открыть канал",

        # === Profile ===
        "profile.referral_id": "👤 <b>Реферал</b> — <code>{id}</code>",
        "btn.replenish": "💳 Пополнить баланс",
        "btn.referral": "🎲 Реферальная система",
        "btn.purchased": "🎁 Купленные товары",

        # === Profile Info Lines ===
        "profile.id": "🆔 <b>ID</b> — <code>{id}</code>",
        "profile.balance": "💳 <b>Баланс</b> — <code>{amount}</code> {currency}",
        "profile.total_topup": "💵 <b>Всего пополнено</b> — <code>{amount}</code> {currency}",
        "profile.purchased_count": "🎁 <b>Куплено товаров</b> — {count} шт",
        "profile.registration_date": "🕢 <b>Дата регистрации</b> — <code>{dt}</code>",

        # === Referral ===
        "referral.title": "💚 Реферальная система",
        "referral.link": "🔗 Ссылка: https://t.me/{bot_username}?start={user_id}",
        "referral.count": "Количество рефералов: {count}",
        "referral.description": (
            "📔 Реферальная система позволит Вам заработать деньги без всяких вложений. "
            "Необходимо всего лишь распространять свою реферальную ссылку и Вы будете получать "
            "{percent}% от суммы пополнений Ваших рефералов на Ваш баланс бота."
        ),

        # === Admin: Main Menu ===
        "admin.menu.main": "⛩️ Меню администратора",
        "admin.menu.shop": "🛒 Управление магазином",
        "admin.menu.goods": "📦 Управление позициями",
        "admin.menu.categories": "📂 Управление категориями",
        "admin.menu.users": "👥 Управление пользователями",
        "admin.menu.broadcast": "📝 Рассылка",
        "admin.menu.rights": "Недостаточно прав",

        # === Admin: User Management ===
        "admin.users.prompt_enter_id": "👤 Введите id пользователя,\nчтобы посмотреть | изменить его данные",
        "admin.users.invalid_id": "⚠️ Введите корректный числовой ID пользователя.",
        "admin.users.profile_unavailable": "❌ Профиль недоступен (такого пользователя никогда не существовало)",
        "admin.users.confirm_view": "Вы точно хотите посмотреть профиль пользователя {id}?",
        "admin.users.not_found": "❌ Пользователь не найден",
        "admin.users.cannot_change_owner": "Нельзя менять роль владельца",
        "admin.users.referrals": "👥 <b>Рефералы пользователя</b> — {count}",
        "admin.users.role": "🎛 <b>Роль</b> — {role}",
        "admin.users.set_admin.success": "✅ Роль присвоена пользователю {name}",
        "admin.users.set_admin.notify": "✅ Вам присвоена роль АДМИНИСТРАТОРА бота",
        "admin.users.remove_admin.success": "✅ Роль отозвана у пользователя {name}",
        "admin.users.remove_admin.notify": "❌ У вас отозвана роль АДМИНИСТРАТОРА бота",
        "admin.users.balance.topped": "✅ Баланс пользователя {name} пополнен на {amount} {currency}",
        "admin.users.balance.topped.notify": "✅ Ваш баланс пополнен на {amount} {currency}",

        # === Admin: Shop Management Menu ===
        "admin.shop.menu.title": "⛩️ Меню управления магазином",
        "admin.shop.menu.statistics": "📊 Статистика",
        "admin.shop.menu.logs": "📁 Показать логи",
        "admin.shop.menu.admins": "👮 Администраторы",
        "admin.shop.menu.users": "👤 Пользователи",
        "admin.shop.menu.search_bought": "🔎 Поиск купленного товара",

        # === Admin: Categories Management ===
        "admin.categories.menu.title": "⛩️ Меню управления категориями",
        "admin.categories.add": "➕ Добавить категорию",
        "admin.categories.rename": "✏️ Переименовать категорию",
        "admin.categories.delete": "🗑 Удалить категорию",
        "admin.categories.prompt.add": "Введите название новой категории:",
        "admin.categories.prompt.delete": "Введите название категории для удаления:",
        "admin.categories.prompt.rename.old": "Введите текущее название категории, которую нужно переименовать:",
        "admin.categories.prompt.rename.new": "Введите новое имя для категории:",
        "admin.categories.add.exist": "❌ Категория не создана (такая уже существует)",
        "admin.categories.add.success": "✅ Категория создана",
        "admin.categories.delete.not_found": "❌ Категория не удалена (такой категории не существует)",
        "admin.categories.delete.success": "✅ Категория удалена",
        "admin.categories.rename.not_found": "❌ Категория не может быть обновлена (такой категории не существует)",
        "admin.categories.rename.exist": "❌ Переименование невозможно (категория с таким именем уже существует)",
        "admin.categories.rename.success": "✅ Категория \"{old}\" переименована в \"{new}\"",

        # === Admin: Goods / Items Management (Add / List / Item Info) ===
        "admin.goods.add_position": "➕ Добавить позицию",
        "admin.goods.add_item": "➕ Добавить товар в позицию",
        "admin.goods.update_position": "📝 Изменить позицию",
        "admin.goods.delete_position": "❌ Удалить позицию",
        "admin.goods.show_items": "📄 Показать товары в позиции",
        "admin.goods.add.prompt.name": "Введите название позиции",
        "admin.goods.add.name.exists": "❌ Позиция не может быть создана (такая позиция уже существует)",
        "admin.goods.add.prompt.description": "Введите описание для позиции:",
        "admin.goods.add.prompt.price": "Введите цену для позиции (число в {currency}):",
        "admin.goods.add.price.invalid": "⚠️ Некорректное значение цены. Введите число.",
        "admin.goods.add.prompt.category": "Введите категорию, к которой будет относиться позиция:",
        "admin.goods.add.category.not_found": "❌ Позиция не может быть создана (категория для привязки введена неверно)",
        "admin.goods.add.infinity.question": "У этой позиции будут бесконечные товары? (всем будет высылаться одна копия значения)",
        "admin.goods.add.values.prompt_multi": (
            "Введите товары для позиции по одному сообщению.\n"
            "Когда закончите ввод — нажмите «Добавить указанные товары»."
        ),
        "admin.goods.add.values.added": "✅ Товар «{value}» добавлен в список ({count} шт.)",
        "admin.goods.add.result.created": "✅ Позиция создана.",
        "admin.goods.add.result.added": "📦 Добавлено товаров: <b>{n}</b>",
        "admin.goods.add.result.skipped_db_dup": "↩️ Пропущено (уже были в БД): <b>{n}</b>",
        "admin.goods.add.result.skipped_batch_dup": "🔁 Пропущено (дубль в вводе): <b>{n}</b>",
        "admin.goods.add.result.skipped_invalid": "🚫 Пропущено (пустые/некорректные): <b>{n}</b>",
        "admin.goods.add.single.prompt_value": "Введите одно значение товара для позиции:",
        "admin.goods.add.single.empty": "⚠️ Значение не может быть пустым.",
        "admin.goods.add.single.created": "✅ Позиция создана, значение добавлено",
        "btn.add_values_finish": "Добавить указанные товары",
        "admin.goods.position.not_found": "❌ Товаров нет (Такой позиции не существует)",
        "admin.goods.list_in_position.empty": "ℹ️ В этой позиции пока нет товаров.",
        "admin.goods.list_in_position.title": "Товары в позиции:",
        "admin.goods.item.invalid": "Некорректные данные",
        "admin.goods.item.invalid_id": "Некорректный ID товара",
        "admin.goods.item.not_found": "Товар не найден",
        "admin.goods.prompt.enter_item_name": "Введите название позиции",
        "admin.goods.menu.title": "⛩️ Меню управления позициями",

        # === Admin: Goods / Items Update Flow ===
        "admin.goods.update.amount.prompt.name": "Введите название позиции",
        "admin.goods.update.amount.not_exists": "❌ Товар не может быть добавлен (такой позиции не существует)",
        "admin.goods.update.amount.infinity_forbidden": "❌ Товар не может быть добавлен (у данной позиции бесконечный товар)",
        "admin.goods.update.values.result.title": "✅ Товары добавлены",
        "admin.goods.update.position.invalid": "Позиция не найдена.",
        "admin.goods.update.position.exists": "Позиция с таким именем уже существует.",
        "admin.goods.update.prompt.name": "Введите название позиции",
        "admin.goods.update.not_exists": "❌ Позиция не может быть изменена (такой позиции не существует)",
        "admin.goods.update.prompt.new_name": "Введите новое имя для позиции:",
        "admin.goods.update.prompt.description": "Введите описание для позиции:",
        "admin.goods.update.infinity.make.question": "Вы хотите сделать товары бесконечными?",
        "admin.goods.update.infinity.deny.question": "Вы хотите отменить бесконечные товары?",
        "admin.goods.update.success": "✅ Позиция обновлена",

        # === Admin: Goods / Items Delete Flow ===
        "admin.goods.delete.prompt.name": "Введите название позиции",
        "admin.goods.delete.position.not_found": "❌ Позиция не удалена (Такой позиции не существует)",
        "admin.goods.delete.position.success": "✅ Позиция удалена",
        "admin.goods.item.delete.button": "❌ Удалить товар",
        "admin.goods.item.already_deleted_or_missing": "Товар уже удалён или не найден",
        "admin.goods.item.deleted": "✅ Товар удалён",

        # === Admin: Item Info ===
        "admin.goods.item.info.position": "<b>Позиция</b>: <code>{name}</code>",
        "admin.goods.item.info.price": "<b>Цена</b>: <code>{price}</code> {currency}",
        "admin.goods.item.info.id": "<b>Уникальный ID</b>: <code>{id}</code>",
        "admin.goods.item.info.value": "<b>Товар</b>: <code>{value}</code>",

        # === Admin: Logs ===
        "admin.shop.logs.caption": "Логи бота",
        "admin.shop.logs.empty": "❗️ Логов пока нет",

        # === Group Notifications ===
        "shop.group.new_upload": "Залив",
        "shop.group.item": "Товар",
        "shop.group.count": "Количество",

        # === Admin: Statistics ===
        "admin.shop.stats.template": (
            "Статистика магазина:\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
            "<b>◽ПОЛЬЗОВАТЕЛИ</b>\n"
            "◾️Пользователей за 24 часа: {today_users}\n"
            "◾️Всего администраторов: {admins}\n"
            "◾️Всего пользователей: {users}\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
            "◽<b>СРЕДСТВА</b>\n"
            "◾Продаж за 24 часа на: {today_orders} {currency}\n"
            "◾Продано товаров на: {all_orders} {currency}\n"
            "◾Пополнений за 24 часа: {today_topups} {currency}\n"
            "◾Средств в системе: {system_balance} {currency}\n"
            "◾Пополнено: {all_topups} {currency}\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
            "◽<b>ПРОЧЕЕ</b>\n"
            "◾Товаров: {items} шт.\n"
            "◾Позиций: {goods} шт.\n"
            "◾Категорий: {categories} шт.\n"
            "◾Продано товаров: {sold_count} шт."
        ),

        # === Admin: Lists & Broadcast ===
        "admin.shop.admins.title": "👮 Администраторы бота:",
        "admin.shop.users.title": "Пользователи бота:",
        "admin.shop.bought.prompt_id": "Введите уникальный ID купленного товара",
        "admin.shop.bought.not_found": "❌ Товар с указанным уникальным ID не найден",
        "broadcast.prompt": "Отправьте сообщение для рассылки:",
        "broadcast.done": "Рассылка завершена. Сообщение отправлено {count} пользователям.",

        # === Payments / Top-up Flow ===
        "payments.replenish_prompt": "Введите сумму пополнения в {currency}:",
        "payments.replenish_invalid": "❌ Неверная сумма. Введите число от {min_amount} до {max_amount} {currency}.",
        "payments.method_choose": "Выберите способ оплаты:",
        "payments.not_configured": "❌ Пополнение не настроено",
        "payments.session_expired": "Сессия оплаты устарела. Начните заново.",
        "payments.crypto.create_fail": "❌ Ошибка при создании счёта: {error}",
        "payments.stars.create_fail": "❌ Не удалось выставить счёт в Stars: {error}",
        "payments.fiat.create_fail": "❌ Не удалось выставить счёт: {error}",
        "payments.no_active_invoice": "❌ Активных счетов не найдено. Начните пополнение заново.",
        "payments.invoice_not_found": "❌ Счёт не найден. Начните заново.",
        "payments.not_paid_yet": "⌛️ Платёж ещё не оплачен.",
        "payments.expired": "❌ Срок действия счёта истёк.",
        "payments.invoice.summary": (
            "💵 Сумма пополнения: {amount} {currency}.\n"
            "⌛️ У вас есть {minutes} минут на оплату.\n"
            "<b>❗️ После оплаты нажмите кнопку «{button}»</b>"
        ),
        "payments.unable_determine_amount": "❌ Не удалось определить сумму оплаты.",
        "payments.topped_simple": "✅ Баланс пополнен на {amount} {currency}",
        "payments.topped_with_suffix": "✅ Баланс пополнен на {amount} {currency} ({suffix})",
        "payments.success_suffix.stars": "Telegram Stars",
        "payments.success_suffix.tg": "Telegram Payments",
        "payments.referral.bonus": "✅ Вы получили {amount} {currency} от вашего реферала {name}",
        "payments.invoice.title.topup": "Пополнение баланса",
        "payments.invoice.label.stars": "{stars} ⭐️",

        # === Shop Browsing (Categories / Goods / Item Page) ===
        "shop.categories.title": "🏪 Категории магазина",
        "shop.goods.choose": "🏪 Выберите нужный товар",
        "shop.item.not_found": "Товар не найден",
        "shop.item.title": "🏪 Товар {name}",
        "shop.item.description": "Описание: {description}",
        "shop.item.price": "Цена — {amount} {currency}",
        "shop.item.quantity_unlimited": "Количество — неограниченно",
        "shop.item.quantity_left": "Количество — {count} шт.",
        "shop.insufficient_funds": "❌ Недостаточно средств",
        "shop.out_of_stock": "❌ Товара нет в наличии",
        "shop.purchase.success": "✅ Товар куплен. <b>Баланс</b>: <i>{balance}</i> {currency}\n\n{value}",

        # === Purchases ===
        "purchases.title": "Купленные товары:",
        "purchases.pagination.invalid": "Некорректные данные пагинации",
        "purchases.item.not_found": "Покупка не найдена",
        "purchases.item.name": "<b>🧾 Товар</b>: <code>{name}</code>",
        "purchases.item.price": "<b>💵 Цена</b>: <code>{amount}</code> {currency}",
        "purchases.item.datetime": "<b>🕒 Дата покупки</b>: <code>{dt}</code>",
        "purchases.item.unique_id": "<b>🧾 Уникальный ID</b>: <code>{uid}</code>",
        "purchases.item.value": "<b>🔑 Значение</b>:\n<code>{value}</code>",
        "purchases.item.buyer": "<b>Покупатель</b>: <code>{buyer}</code>",

        # === Errors ===
        "errors.not_subscribed": "Вы не подписались",
        "errors.something_wrong": "❌ Что-то пошло не так. Попробуйте ещё раз.",
        "errors.pagination_invalid": "Некорректные данные пагинации",
        "errors.invalid_data": "❌ Неправильные данные",
        "errors.id_should_be_number": "❌ ID должен быть числом.",
}