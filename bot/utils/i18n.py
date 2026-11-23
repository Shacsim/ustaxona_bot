"""Bot interfeysi uchun uch tillik (uz/ru/en) matnlar.

Guruhga chiqadigan mijoz xabarlari formatters.py da 3 tilda bir xabarda
turadi. Bu modul botning usta/admin bilan shaxsiy muloqoti uchun.
"""

LANGS = ("uz", "ru", "en")
LANG_NAMES = {"uz": "O'zbekcha 🇺🇿", "ru": "Русский 🇷🇺", "en": "English 🇬🇧"}


def _l(uz: str, ru: str, en: str) -> dict[str, str]:
    return {"uz": uz, "ru": ru, "en": en}


def norm_lang(lang: str | None) -> str:
    return lang if lang in LANGS else "uz"


# ---------- Tugmalar (reply keyboard) ----------
# Handler'lar barcha til variantlarini qabul qilishi uchun btn_variants() bor.

BUTTONS = {
    "new_order": _l("➕ Yangi buyurtma", "➕ Новый заказ", "➕ New order"),
    "complete": _l("🛠 Buyurtmani tayyor qilish", "🛠 Заказ готов", "🛠 Complete order"),
    "pending": _l("📋 Kutayotgan buyurtmalar", "📋 Заказы в ожидании", "📋 Pending orders"),
    "ready_list": _l("✅ Tayyor buyurtmalar", "✅ Готовые заказы", "✅ Ready orders"),
    "search": _l("🔎 Buyurtmani topish", "🔎 Найти заказ", "🔎 Find order"),
    "my_income": _l("💰 Daromadim", "💰 Мой доход", "💰 My income"),
    "inventory": _l("📦 Omborim", "📦 Мой склад", "📦 My stock"),
    "profile": _l("👤 Profil", "👤 Профиль", "👤 Profile"),
    "admin": _l("⚙️ Admin panel", "⚙️ Admin panel", "⚙️ Admin panel"),
    "cancel": _l("❌ Bekor qilish", "❌ Отмена", "❌ Cancel"),
    "confirm_accept": _l("✅ Qabul qilindi", "✅ Принять", "✅ Accept"),
    "confirm_ready": _l("✅ TAYYOR", "✅ ГОТОВО", "✅ READY"),
    "confirm": _l("✅ Tasdiqlash", "✅ Подтвердить", "✅ Confirm"),
    "back": _l("⬅️ Orqaga", "⬅️ Назад", "⬅️ Back"),
    "dial_phone": _l("📱 Raqamni terish", "📱 Набрать номер", "📱 Dial number"),
}


def btn(key: str, lang: str) -> str:
    variants = BUTTONS[key]
    return variants.get(lang, variants["uz"])


def btn_variants(key: str) -> set[str]:
    return set(BUTTONS[key].values())


# ---------- Matnlar ----------

TEXTS = {
    # Til tanlash / registratsiya
    "choose_language": _l(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
    ),
    "lang_set": _l("✅ Til: O'zbekcha 🇺🇿", "✅ Язык: Русский 🇷🇺", "✅ Language: English 🇬🇧"),
    "reg_ask_name": _l(
        "Assalomu alaykum!\n\n"
        "Kompyuter servis boshqaruv botiga xush kelibsiz.\n\n"
        "Avval tizimda ro'yxatdan o'tishingiz kerak.\n\n"
        "Iltimos, ismingizni kiriting:",
        "Здравствуйте!\n\n"
        "Добро пожаловать в бот управления компьютерным сервисом.\n\n"
        "Сначала нужно зарегистрироваться.\n\n"
        "Пожалуйста, введите ваше имя:",
        "Hello!\n\n"
        "Welcome to the computer service management bot.\n\n"
        "First you need to register.\n\n"
        "Please enter your name:",
    ),
    "reg_name_invalid": _l(
        "❌ Ism 2 tadan 50 tagacha belgidan iborat bo'lishi kerak.\nQayta kiriting:",
        "❌ Имя должно содержать от 2 до 50 символов.\nВведите ещё раз:",
        "❌ The name must be 2 to 50 characters long.\nPlease try again:",
    ),
    "reg_already": _l(
        "Siz allaqachon ro'yxatdan o'tgansiz.",
        "Вы уже зарегистрированы.",
        "You are already registered.",
    ),
    "reg_wait_approval": _l(
        "✅ Rahmat, <b>{name}</b>!\n\n"
        "Ma'lumotlaringiz qabul qilindi.\n"
        "⏳ Administrator profilingizni tasdiqlagach, sizga xabar beramiz.",
        "✅ Спасибо, <b>{name}</b>!\n\n"
        "Ваши данные приняты.\n"
        "⏳ Как только администратор подтвердит ваш профиль, мы сообщим вам.",
        "✅ Thank you, <b>{name}</b>!\n\n"
        "Your details have been received.\n"
        "⏳ We will let you know once an administrator approves your profile.",
    ),
    "reg_admin_welcome": _l(
        "✅ Xush kelibsiz, <b>{name}</b>!\n\n"
        "Siz <b>administrator</b> sifatida ro'yxatdan o'tdingiz.",
        "✅ Добро пожаловать, <b>{name}</b>!\n\n"
        "Вы зарегистрированы как <b>администратор</b>.",
        "✅ Welcome, <b>{name}</b>!\n\n"
        "You are registered as an <b>administrator</b>.",
    ),
    "welcome_back": _l(
        "Xush kelibsiz, <b>{name}</b>! 👋",
        "С возвращением, <b>{name}</b>! 👋",
        "Welcome back, <b>{name}</b>! 👋",
    ),
    "pending_approval": _l(
        "⏳ Profilingiz administrator tasdig'ini kutmoqda.\n"
        "Tasdiqlangach sizga xabar beramiz.",
        "⏳ Ваш профиль ожидает подтверждения администратора.\n"
        "Мы сообщим вам после подтверждения.",
        "⏳ Your profile is waiting for administrator approval.\n"
        "We will notify you once it is approved.",
    ),
    "approved_notice": _l(
        "🎉 Profilingiz administrator tomonidan tasdiqlandi!\n\n"
        "Endi tizimdan to'liq foydalanishingiz mumkin.",
        "🎉 Ваш профиль подтверждён администратором!\n\n"
        "Теперь вы можете полноценно пользоваться системой.",
        "🎉 Your profile has been approved by an administrator!\n\n"
        "You now have full access to the system.",
    ),
    "blocked_notice": _l(
        "⛔️ Profilingiz administrator tomonidan bloklandi.",
        "⛔️ Ваш профиль заблокирован администратором.",
        "⛔️ Your profile has been blocked by an administrator.",
    ),

    # Umumiy
    "cancelled": _l("❌ Amal bekor qilindi.", "❌ Действие отменено.", "❌ Action cancelled."),
    "use_menu": _l(
        "Quyidagi menyudan foydalaning 👇",
        "Используйте меню ниже 👇",
        "Use the menu below 👇",
    ),
    "continue": _l("Davom etamiz 👇", "Продолжаем 👇", "Let's continue 👇"),
    "fsm_hint": _l(
        "Iltimos, so'ralgan ma'lumotni matn ko'rinishida yuboring "
        "yoki «❌ Bekor qilish» tugmasini bosing.",
        "Пожалуйста, отправьте запрошенные данные текстом "
        "или нажмите «❌ Отмена».",
        "Please send the requested information as text "
        "or press «❌ Cancel».",
    ),
    "menu_placeholder": _l("Amalni tanlang…", "Выберите действие…", "Choose an action…"),
    "open_app": _l("📱 Ilovani ochish", "📱 Открыть приложение", "📱 Open the app"),
    "app_hint": _l(
        "📱 Botni ilova ko'rinishida ham ishlatishingiz mumkin — pastdagi tugma yoki "
        "chatdagi «📱 Ilova» menyu tugmasi orqali.",
        "📱 Ботом можно пользоваться и как приложением — кнопка ниже или "
        "кнопка меню «📱 Ilova» в чате.",
        "📱 You can also use the bot as an app — the button below or "
        "the «📱 Ilova» menu button in the chat.",
    ),
    "session_expired": _l(
        "⌛️ Bu amal eskirgan. Menyudan qaytadan boshlang.",
        "⌛️ Это действие устарело. Начните заново из меню.",
        "⌛️ This action has expired. Please start again from the menu.",
    ),

    # Yangi buyurtma oqimi: telefon → ism → vazifa
    "ask_customer_phone": _l(
        "📥 <b>Yangi buyurtma</b>\n\n"
        "📞 Mijoz telefon raqamini kiriting.\n\n"
        "«📱 Raqamni terish» tugmasi sonli klaviaturani ochadi. "
        "Raqamni shu yerga yozishingiz yoki kontaktni ulashishingiz ham mumkin.\n\n"
        "Masalan: <b>901234567</b> yoki <b>+998901234567</b>",
        "📥 <b>Новый заказ</b>\n\n"
        "📞 Введите номер телефона клиента.\n\n"
        "Кнопка «📱 Набрать номер» открывает цифровую клавиатуру. "
        "Можно также написать номер здесь или поделиться контактом.\n\n"
        "Например: <b>901234567</b> или <b>+998901234567</b>",
        "📥 <b>New order</b>\n\n"
        "📞 Enter the customer's phone number.\n\n"
        "The «📱 Dial number» button opens a numeric keypad. "
        "You can also type the number here or share a contact.\n\n"
        "Example: <b>901234567</b> or <b>+998901234567</b>",
    ),
    "invalid_phone": _l(
        "❌ Telefon raqami noto'g'ri.\n"
        "Faqat raqamlar (va boshida +) bo'lsin.\n\n"
        "Masalan: <b>901234567</b> yoki <b>+998901234567</b>",
        "❌ Неверный номер телефона.\n"
        "Только цифры (и + в начале).\n\n"
        "Например: <b>901234567</b> или <b>+998901234567</b>",
        "❌ Invalid phone number.\n"
        "Digits only (and + at the start).\n\n"
        "Example: <b>901234567</b> or <b>+998901234567</b>",
    ),
    "ask_customer_name": _l(
        "📞 Telefon: <b>{phone}</b>\n\n👤 Mijoz ismini kiriting:",
        "📞 Телефон: <b>{phone}</b>\n\n👤 Введите имя клиента:",
        "📞 Phone: <b>{phone}</b>\n\n👤 Enter the customer's name:",
    ),
    "customer_known": _l(
        "ℹ️ Bu raqam bazada bor: <b>{name}</b> ({count} ta oldingi buyurtma).\n"
        "Pastdagi tugmani bosing yoki boshqa ism yozing.",
        "ℹ️ Этот номер уже есть в базе: <b>{name}</b> (прошлых заказов: {count}).\n"
        "Нажмите кнопку ниже или напишите другое имя.",
        "ℹ️ This number is already known: <b>{name}</b> ({count} previous orders).\n"
        "Tap the button below or type another name.",
    ),
    "contact_name_hint": _l(
        "ℹ️ Kontaktdagi ism: <b>{name}</b> — pastdagi tugmani bosing yoki boshqa ism yozing.",
        "ℹ️ Имя из контакта: <b>{name}</b> — нажмите кнопку ниже или напишите другое имя.",
        "ℹ️ Name from the contact: <b>{name}</b> — tap the button below or type another name.",
    ),
    "invalid_customer_name": _l(
        "❌ Ism 2 tadan 50 tagacha belgidan iborat bo'lishi kerak.\nQayta kiriting:",
        "❌ Имя должно содержать от 2 до 50 символов.\nВведите ещё раз:",
        "❌ The name must be 2 to 50 characters long.\nPlease try again:",
    ),
    "ask_description": _l(
        "🔧 Nima qilish kerak?\n\nMuammo/vazifani qisqacha yozing:",
        "🔧 Что нужно сделать?\n\nКоротко опишите проблему/задачу:",
        "🔧 What needs to be done?\n\nBriefly describe the problem/task:",
    ),
    "invalid_description": _l(
        "❌ Tavsif juda qisqa yoki juda uzun (3–500 belgi). Qayta yozing:",
        "❌ Описание слишком короткое или длинное (3–500 символов). Напишите ещё раз:",
        "❌ The description is too short or too long (3–500 characters). Try again:",
    ),
    "order_summary": _l(
        "🧾 <b>YANGI BUYURTMA</b>\n\n"
        "🔢 Buyurtma raqami: <b>#{n}</b> (avtomatik)\n"
        "📞 Telefon: <b>{phone}</b>\n"
        "👤 Mijoz: <b>{name}</b>\n"
        "🔧 Vazifa: {task}\n\n"
        "Buyurtma qabul qilinsinmi?",
        "🧾 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        "🔢 Номер заказа: <b>#{n}</b> (автоматически)\n"
        "📞 Телефон: <b>{phone}</b>\n"
        "👤 Клиент: <b>{name}</b>\n"
        "🔧 Задача: {task}\n\n"
        "Принять заказ?",
        "🧾 <b>NEW ORDER</b>\n\n"
        "🔢 Order number: <b>#{n}</b> (automatic)\n"
        "📞 Phone: <b>{phone}</b>\n"
        "👤 Customer: <b>{name}</b>\n"
        "🔧 Task: {task}\n\n"
        "Accept the order?",
    ),
    "order_created": _l(
        "✅ Buyurtma <b>#{n}</b> qabul qilindi!\n\n{note}",
        "✅ Заказ <b>#{n}</b> принят!\n\n{note}",
        "✅ Order <b>#{n}</b> accepted!\n\n{note}",
    ),
    "group_sent_pending": _l(
        "📤 Guruhdagi «Kutayotgan buyurtmalar» bo'limiga e'lon yuborildi.",
        "📤 Объявление отправлено в раздел «Kutayotganlar» группы.",
        "📤 The announcement was posted to the group's «Pending orders» topic.",
    ),
    "group_send_failed": _l(
        "⚠️ Guruhga e'lon yuborib bo'lmadi (sozlamalarni tekshiring). "
        "Buyurtma bazaga saqlandi.",
        "⚠️ Не удалось отправить объявление в группу (проверьте настройки). "
        "Заказ сохранён в базе.",
        "⚠️ Could not post to the group (check the settings). "
        "The order is saved in the database.",
    ),
    "order_create_cancelled": _l(
        "❌ Buyurtma yaratish bekor qilindi.",
        "❌ Создание заказа отменено.",
        "❌ Order creation cancelled.",
    ),

    # Buyurtmani tayyor qilish oqimi
    "ask_ready_number": _l(
        "🔢 Tayyor bo'lgan buyurtma raqamini kiriting:",
        "🔢 Введите номер готового заказа:",
        "🔢 Enter the number of the completed order:",
    ),
    "invalid_number": _l(
        "❌ Buyurtma raqami faqat raqamlardan iborat bo'lishi kerak.\n\nMasalan: <b>27</b>",
        "❌ Номер заказа должен состоять только из цифр.\n\nНапример: <b>27</b>",
        "❌ The order number must contain digits only.\n\nExample: <b>27</b>",
    ),
    "order_not_found": _l(
        "❌ <b>#{n}</b> raqamli buyurtma topilmadi.\n\nRaqamni tekshirib qayta kiriting.",
        "❌ Заказ <b>#{n}</b> не найден.\n\nПроверьте номер и введите ещё раз.",
        "❌ Order <b>#{n}</b> was not found.\n\nCheck the number and try again.",
    ),
    "already_ready": _l(
        "ℹ️ <b>#{n}</b> raqamli buyurtma allaqachon tayyor deb belgilangan.",
        "ℹ️ Заказ <b>#{n}</b> уже отмечен как готовый.",
        "ℹ️ Order <b>#{n}</b> is already marked as ready.",
    ),
    "was_cancelled": _l(
        "ℹ️ <b>#{n}</b> raqamli buyurtma bekor qilingan.",
        "ℹ️ Заказ <b>#{n}</b> был отменён.",
        "ℹ️ Order <b>#{n}</b> was cancelled.",
    ),
    "ask_work_done": _l(
        "🔧 <b>Buyurtma #{n}</b>\n\n"
        "Qanday ishlar bajarildi?\n\n"
        "Bajarilgan ishlarni batafsil yozing (har birini yangi qatordan):",
        "🔧 <b>Заказ #{n}</b>\n\n"
        "Какие работы выполнены?\n\n"
        "Опишите выполненные работы подробно (каждую с новой строки):",
        "🔧 <b>Order #{n}</b>\n\n"
        "What work was done?\n\n"
        "Describe the work in detail (each item on a new line):",
    ),
    "work_too_short": _l(
        "❌ Bajarilgan ishlar tavsifi juda qisqa. Batafsilroq yozing:",
        "❌ Описание работ слишком короткое. Напишите подробнее:",
        "❌ The work description is too short. Please add more detail:",
    ),
    "work_too_long": _l(
        "❌ Tavsif juda uzun (maksimum 2000 belgi). Qisqartiring:",
        "❌ Описание слишком длинное (максимум 2000 символов). Сократите:",
        "❌ The description is too long (max 2000 characters). Please shorten it:",
    ),
    "ask_price": _l(
        "💰 Xizmat haqqini kiriting:\n\nMasalan:\n<b>250000</b>",
        "💰 Введите стоимость услуги:\n\nНапример:\n<b>250000</b>",
        "💰 Enter the service price:\n\nExample:\n<b>250000</b>",
    ),
    "invalid_price": _l(
        "❌ Iltimos, summani faqat raqam bilan kiriting.\n\nMasalan:\n<b>250000</b>",
        "❌ Пожалуйста, введите сумму только цифрами.\n\nНапример:\n<b>250000</b>",
        "❌ Please enter the amount using digits only.\n\nExample:\n<b>250000</b>",
    ),
    "ready_summary": _l(
        "📋 <b>Buyurtma #{n}</b>\n\n"
        "🔧 <b>Bajarilgan ishlar:</b>\n{work}\n\n"
        "💰 Xizmat haqqi: <b>{price}</b>\n\n"
        "Buyurtma tayyormi?",
        "📋 <b>Заказ #{n}</b>\n\n"
        "🔧 <b>Выполненные работы:</b>\n{work}\n\n"
        "💰 Стоимость: <b>{price}</b>\n\n"
        "Заказ готов?",
        "📋 <b>Order #{n}</b>\n\n"
        "🔧 <b>Work done:</b>\n{work}\n\n"
        "💰 Price: <b>{price}</b>\n\n"
        "Is the order ready?",
    ),
    "ready_done": _l(
        "✅ Buyurtma <b>#{n}</b> tayyor deb belgilandi!\n\n{note}",
        "✅ Заказ <b>#{n}</b> отмечен как готовый!\n\n{note}",
        "✅ Order <b>#{n}</b> marked as ready!\n\n{note}",
    ),
    "group_sent_ready": _l(
        "📤 Guruhdagi «Tayyor buyurtmalar» bo'limiga e'lon yuborildi.",
        "📤 Объявление отправлено в раздел «Tayyorlar» группы.",
        "📤 The announcement was posted to the group's «Ready orders» topic.",
    ),
    "group_send_failed_ready": _l(
        "⚠️ Guruhga e'lon yuborib bo'lmadi (sozlamalarni tekshiring). "
        "Buyurtma bazada TAYYOR deb belgilandi.",
        "⚠️ Не удалось отправить объявление в группу (проверьте настройки). "
        "Заказ отмечен как ГОТОВЫЙ в базе.",
        "⚠️ Could not post to the group (check the settings). "
        "The order is marked READY in the database.",
    ),
    "complete_cancelled": _l(
        "❌ Amal bekor qilindi. Buyurtma o'zgartirilmadi.",
        "❌ Действие отменено. Заказ не изменён.",
        "❌ Cancelled. The order was not changed.",
    ),
    "order_vanished": _l(
        "❌ Buyurtma topilmadi. Qaytadan urinib ko'ring.",
        "❌ Заказ не найден. Попробуйте ещё раз.",
        "❌ Order not found. Please try again.",
    ),

    # Qidiruv va ro'yxatlar
    "search_prompt": _l(
        "🔎 Buyurtma raqamini kiriting:",
        "🔎 Введите номер заказа:",
        "🔎 Enter the order number:",
    ),
    "search_not_found": _l(
        "❌ <b>#{n}</b> raqamli buyurtma topilmadi.\n\nBoshqa raqam kiriting yoki bekor qiling.",
        "❌ Заказ <b>#{n}</b> не найден.\n\nВведите другой номер или отмените.",
        "❌ Order <b>#{n}</b> was not found.\n\nEnter another number or cancel.",
    ),
    "ready_header": _l(
        "✅ <b>TAYYOR BUYURTMALAR</b> (oxirgi 10 ta)\n",
        "✅ <b>ГОТОВЫЕ ЗАКАЗЫ</b> (последние 10)\n",
        "✅ <b>READY ORDERS</b> (last 10)\n",
    ),
    "none_pending": _l(
        "📋 Hozircha kutayotgan buyurtmalar yo'q.",
        "📋 Пока нет заказов в ожидании.",
        "📋 There are no pending orders right now.",
    ),
    "none_ready": _l(
        "✅ Hozircha tayyor buyurtmalar yo'q.",
        "✅ Пока нет готовых заказов.",
        "✅ There are no ready orders yet.",
    ),
    "pdf_offer": _l(
        "📄 PDF hisobot kerakmi?",
        "📄 Нужен отчёт в PDF?",
        "📄 Need a PDF report?",
    ),
    "pdf_ready_offer": _l(
        "📄 Tayyor buyurtmalar bo'yicha PDF hisobot — davrni tanlang:",
        "📄 PDF-отчёт по готовым заказам — выберите период:",
        "📄 PDF report of ready orders — choose a period:",
    ),
    "pdf_making": _l("⏳ PDF tayyorlanmoqda…", "⏳ Готовлю PDF…", "⏳ Preparing the PDF…"),
    "pdf_empty": _l(
        "ℹ️ Bu davrda ma'lumot yo'q.",
        "ℹ️ За этот период данных нет.",
        "ℹ️ No data for this period.",
    ),
    "pdf_btn": _l("📄 PDF hisobot", "📄 PDF-отчёт", "📄 PDF report"),

    # Profil
    "profile_card": _l(
        "👤 <b>PROFIL</b>\n\n"
        "Ism: <b>{name}</b>\n"
        "Rol: {role}\n"
        "Til: {language}\n"
        "Telegram ID: <code>{tg_id}</code>\n"
        "Ro'yxatdan o'tgan: {created}\n\n"
        "Tilni almashtirish: /start",
        "👤 <b>ПРОФИЛЬ</b>\n\n"
        "Имя: <b>{name}</b>\n"
        "Роль: {role}\n"
        "Язык: {language}\n"
        "Telegram ID: <code>{tg_id}</code>\n"
        "Зарегистрирован: {created}\n\n"
        "Сменить язык: /start",
        "👤 <b>PROFILE</b>\n\n"
        "Name: <b>{name}</b>\n"
        "Role: {role}\n"
        "Language: {language}\n"
        "Telegram ID: <code>{tg_id}</code>\n"
        "Registered: {created}\n\n"
        "Change language: /start",
    ),
    "role_admin": _l("👑 Administrator", "👑 Администратор", "👑 Administrator"),
    "role_master": _l("🔧 Usta", "🔧 Мастер", "🔧 Technician"),

    # Daromad hisoboti
    "income_header": _l(
        "💰 <b>DAROMADIM</b>\n👨‍🔧 {name}\n",
        "💰 <b>МОЙ ДОХОД</b>\n👨‍🔧 {name}\n",
        "💰 <b>MY INCOME</b>\n👨‍🔧 {name}\n",
    ),
    "income_row": _l(
        "{icon} {label}: <b>{total}</b> — {count} ta buyurtma",
        "{icon} {label}: <b>{total}</b> — заказов: {count}",
        "{icon} {label}: <b>{total}</b> — {count} orders",
    ),
    "income_sales_row": _l(
        "🛒 Bugun ombordan sotuv: <b>{total}</b> (foyda {profit})",
        "🛒 Продажи со склада сегодня: <b>{total}</b> (прибыль {profit})",
        "🛒 Stock sales today: <b>{total}</b> (profit {profit})",
    ),
    "period_today": _l("Bugun", "Сегодня", "Today"),
    "period_week": _l("Shu hafta", "Эта неделя", "This week"),
    "period_month": _l("Shu oy", "Этот месяц", "This month"),
    "period_all": _l("Jami (hozirgacha)", "Всего (за всё время)", "All time"),
    "period_btn_today": _l("📅 Bugun", "📅 Сегодня", "📅 Today"),
    "period_btn_week": _l("🗓 Hafta", "🗓 Неделя", "🗓 Week"),
    "period_btn_month": _l("📆 Oy", "📆 Месяц", "📆 Month"),
    "period_btn_all": _l("∑ Jami", "∑ Всё", "∑ All"),

    # ---------- Ombor ----------
    "inv_title": _l(
        "📦 <b>OMBORIM</b>\n\n"
        "Mahsulot turlari: <b>{kinds}</b> · Jami: <b>{units}</b> dona\n"
        "Ombor qiymati (tannarxda): <b>{value}</b>\n\n"
        "📅 Bugun:\n"
        "📥 Sotib olindi: {in_units} dona — {in_sum}\n"
        "📤 Sotildi: {out_units} dona — {out_sum} (foyda {profit})",
        "📦 <b>МОЙ СКЛАД</b>\n\n"
        "Видов товара: <b>{kinds}</b> · Всего: <b>{units}</b> шт.\n"
        "Стоимость склада (по себестоимости): <b>{value}</b>\n\n"
        "📅 Сегодня:\n"
        "📥 Куплено: {in_units} шт. — {in_sum}\n"
        "📤 Продано: {out_units} шт. — {out_sum} (прибыль {profit})",
        "📦 <b>MY STOCK</b>\n\n"
        "Product types: <b>{kinds}</b> · Total: <b>{units}</b> pcs\n"
        "Stock value (at cost): <b>{value}</b>\n\n"
        "📅 Today:\n"
        "📥 Bought: {in_units} pcs — {in_sum}\n"
        "📤 Sold: {out_units} pcs — {out_sum} (profit {profit})",
    ),
    "inv_btn_buy": _l("📥 Sotib oldim", "📥 Купил", "📥 I bought"),
    "inv_btn_sell": _l("📤 Sotdim", "📤 Продал", "📤 I sold"),
    "inv_btn_stock": _l("📦 Qoldiq", "📦 Остатки", "📦 In stock"),
    "inv_btn_buys": _l("🧾 Sotib olinganlar", "🧾 Покупки", "🧾 Purchases"),
    "inv_btn_sales": _l("💸 Sotilganlar", "💸 Продажи", "💸 Sales"),
    "inv_btn_undo": _l("↩️ Oxirgi yozuvni bekor qilish", "↩️ Отменить последнюю запись", "↩️ Undo last entry"),
    "inv_btn_new": _l("➕ Yangi mahsulot", "➕ Новый товар", "➕ New product"),
    "inv_pick_buy": _l(
        "📥 <b>Sotib oldim</b>\n\nQaysi mahsulot? Ro'yxatdan tanlang yoki yangisini qo'shing:",
        "📥 <b>Купил</b>\n\nКакой товар? Выберите из списка или добавьте новый:",
        "📥 <b>I bought</b>\n\nWhich product? Pick one from the list or add a new one:",
    ),
    "inv_pick_sell": _l(
        "📤 <b>Sotdim</b>\n\nQaysi mahsulot sotildi?",
        "📤 <b>Продал</b>\n\nКакой товар продан?",
        "📤 <b>I sold</b>\n\nWhich product was sold?",
    ),
    "inv_nothing_to_sell": _l(
        "ℹ️ Omboringiz bo'sh — avval «📥 Sotib oldim» orqali mahsulot qo'shing.",
        "ℹ️ Склад пуст — сначала добавьте товар через «📥 Купил».",
        "ℹ️ Your stock is empty — add products first via «📥 I bought».",
    ),
    "inv_ask_name": _l(
        "✏️ Mahsulot nomini yozing.\n\nMasalan: <b>SSD 256GB Kingston</b> yoki <b>RAM DDR4 8GB</b>",
        "✏️ Напишите название товара.\n\nНапример: <b>SSD 256GB Kingston</b> или <b>RAM DDR4 8GB</b>",
        "✏️ Type the product name.\n\nExample: <b>SSD 256GB Kingston</b> or <b>RAM DDR4 8GB</b>",
    ),
    "inv_invalid_name": _l(
        "❌ Nom 2 tadan 100 tagacha belgi bo'lsin. Qayta yozing:",
        "❌ Название должно быть от 2 до 100 символов. Напишите ещё раз:",
        "❌ The name must be 2 to 100 characters. Try again:",
    ),
    "inv_ask_buy_qty": _l(
        "📦 <b>{name}</b>\n\nNechta sotib oldingiz? (omborda hozir: {stock} ta)",
        "📦 <b>{name}</b>\n\nСколько штук купили? (сейчас на складе: {stock})",
        "📦 <b>{name}</b>\n\nHow many did you buy? (in stock now: {stock})",
    ),
    "inv_ask_sell_qty": _l(
        "📦 <b>{name}</b>\n\nNechta sotildi? (omborda: {stock} ta)",
        "📦 <b>{name}</b>\n\nСколько продано? (на складе: {stock})",
        "📦 <b>{name}</b>\n\nHow many were sold? (in stock: {stock})",
    ),
    "inv_invalid_qty": _l(
        "❌ Sonini butun raqam bilan kiriting (1–100000).",
        "❌ Введите количество целым числом (1–100000).",
        "❌ Enter the quantity as a whole number (1–100000).",
    ),
    "inv_not_enough": _l(
        "❌ Omborda faqat {stock} ta bor. Kamroq son kiriting:",
        "❌ На складе только {stock} шт. Введите меньшее число:",
        "❌ Only {stock} in stock. Enter a smaller number:",
    ),
    "inv_ask_buy_price": _l(
        "💵 Bir donasini necha so'mdan oldingiz?\n\nMasalan: <b>250000</b>",
        "💵 Почём купили одну штуку (сум)?\n\nНапример: <b>250000</b>",
        "💵 What was the price per unit (UZS)?\n\nExample: <b>250000</b>",
    ),
    "inv_ask_sell_price": _l(
        "💵 Bir donasini necha so'mdan sotdingiz?\n\nMasalan: <b>320000</b>",
        "💵 Почём продали одну штуку (сум)?\n\nНапример: <b>320000</b>",
        "💵 What was the sale price per unit (UZS)?\n\nExample: <b>320000</b>",
    ),
    "inv_buy_summary": _l(
        "📥 <b>SOTIB OLINDI</b>\n\n"
        "📦 {name}\n"
        "🔢 Soni: <b>{qty}</b> ta\n"
        "💵 Narxi: {price} / dona\n"
        "∑ Jami: <b>{total}</b>\n\n"
        "Omborga qo'shilsinmi?",
        "📥 <b>ПОКУПКА</b>\n\n"
        "📦 {name}\n"
        "🔢 Количество: <b>{qty}</b>\n"
        "💵 Цена: {price} / шт.\n"
        "∑ Итого: <b>{total}</b>\n\n"
        "Добавить на склад?",
        "📥 <b>PURCHASE</b>\n\n"
        "📦 {name}\n"
        "🔢 Quantity: <b>{qty}</b>\n"
        "💵 Price: {price} / pc\n"
        "∑ Total: <b>{total}</b>\n\n"
        "Add to stock?",
    ),
    "inv_sell_summary": _l(
        "📤 <b>SOTILDI</b>\n\n"
        "📦 {name}\n"
        "🔢 Soni: <b>{qty}</b> ta\n"
        "💵 Narxi: {price} / dona\n"
        "∑ Jami: <b>{total}</b>\n"
        "📈 Taxminiy foyda: {profit}\n\n"
        "Sotuv yozilsinmi?",
        "📤 <b>ПРОДАЖА</b>\n\n"
        "📦 {name}\n"
        "🔢 Количество: <b>{qty}</b>\n"
        "💵 Цена: {price} / шт.\n"
        "∑ Итого: <b>{total}</b>\n"
        "📈 Примерная прибыль: {profit}\n\n"
        "Записать продажу?",
        "📤 <b>SALE</b>\n\n"
        "📦 {name}\n"
        "🔢 Quantity: <b>{qty}</b>\n"
        "💵 Price: {price} / pc\n"
        "∑ Total: <b>{total}</b>\n"
        "📈 Estimated profit: {profit}\n\n"
        "Record the sale?",
    ),
    "inv_buy_saved": _l(
        "✅ Omborga qo'shildi: <b>{name}</b> × {qty}\n📦 Endi omborda: <b>{stock}</b> ta\n🕐 {when}",
        "✅ Добавлено на склад: <b>{name}</b> × {qty}\n📦 Теперь на складе: <b>{stock}</b>\n🕐 {when}",
        "✅ Added to stock: <b>{name}</b> × {qty}\n📦 Now in stock: <b>{stock}</b>\n🕐 {when}",
    ),
    "inv_sell_saved": _l(
        "✅ Sotuv yozildi: <b>{name}</b> × {qty} — {total}\n📦 Omborda qoldi: <b>{stock}</b> ta\n🕐 {when}",
        "✅ Продажа записана: <b>{name}</b> × {qty} — {total}\n📦 Осталось на складе: <b>{stock}</b>\n🕐 {when}",
        "✅ Sale recorded: <b>{name}</b> × {qty} — {total}\n📦 Left in stock: <b>{stock}</b>\n🕐 {when}",
    ),
    "inv_cancelled": _l(
        "❌ Bekor qilindi. Ombor o'zgarmadi.",
        "❌ Отменено. Склад не изменён.",
        "❌ Cancelled. Stock was not changed.",
    ),
    "inv_stock_header": _l(
        "📦 <b>OMBORDAGI QOLDIQ</b>\n",
        "📦 <b>ОСТАТКИ НА СКЛАДЕ</b>\n",
        "📦 <b>CURRENT STOCK</b>\n",
    ),
    "inv_stock_row": _l(
        "• <b>{name}</b> — {qty} ta · tannarx {cost}",
        "• <b>{name}</b> — {qty} шт. · себест. {cost}",
        "• <b>{name}</b> — {qty} pcs · cost {cost}",
    ),
    "inv_stock_total": _l(
        "\n∑ Jami: <b>{units}</b> dona · qiymati <b>{value}</b>",
        "\n∑ Всего: <b>{units}</b> шт. · стоимость <b>{value}</b>",
        "\n∑ Total: <b>{units}</b> pcs · value <b>{value}</b>",
    ),
    "inv_stock_empty": _l(
        "📦 Omboringiz hozircha bo'sh.",
        "📦 Ваш склад пока пуст.",
        "📦 Your stock is empty for now.",
    ),
    "inv_buys_header": _l(
        "🧾 <b>SOTIB OLINGANLAR</b> (oxirgi {n} ta)\n",
        "🧾 <b>ПОКУПКИ</b> (последние {n})\n",
        "🧾 <b>PURCHASES</b> (last {n})\n",
    ),
    "inv_sales_header": _l(
        "💸 <b>SOTILGANLAR</b> (oxirgi {n} ta)\n",
        "💸 <b>ПРОДАЖИ</b> (последние {n})\n",
        "💸 <b>SALES</b> (last {n})\n",
    ),
    "inv_moves_empty": _l(
        "ℹ️ Hozircha yozuvlar yo'q.",
        "ℹ️ Записей пока нет.",
        "ℹ️ No entries yet.",
    ),
    "inv_undo_confirm": _l(
        "↩️ Oxirgi yozuv bekor qilinsinmi?\n\n{move}",
        "↩️ Отменить последнюю запись?\n\n{move}",
        "↩️ Undo the last entry?\n\n{move}",
    ),
    "inv_undo_done": _l(
        "✅ Yozuv bekor qilindi. <b>{name}</b> — omborda endi {stock} ta.",
        "✅ Запись отменена. <b>{name}</b> — теперь на складе {stock}.",
        "✅ Entry undone. <b>{name}</b> — now {stock} in stock.",
    ),
    "inv_undo_none": _l(
        "ℹ️ Bekor qilinadigan yozuv yo'q.",
        "ℹ️ Нет записей для отмены.",
        "ℹ️ There is nothing to undo.",
    ),
    "inv_undo_impossible": _l(
        "❌ Bekor qilib bo'lmaydi: bu mahsulotdan allaqachon sotilgan (qoldiq manfiy bo'lib qoladi).",
        "❌ Нельзя отменить: часть этого товара уже продана (остаток станет отрицательным).",
        "❌ Cannot undo: some of this product has already been sold (stock would go negative).",
    ),
    "inv_pdf_offer": _l(
        "📄 PDF hisobot (daromad + ombor) — davrni tanlang:",
        "📄 PDF-отчёт (доход + склад) — выберите период:",
        "📄 PDF report (income + stock) — choose a period:",
    ),
    "move_in": _l("📥 Kirim", "📥 Приход", "📥 In"),
    "move_out": _l("📤 Sotuv", "📤 Продажа", "📤 Sale"),

    # ---------- Kunlik hisobot ----------
    "daily_caption": _l(
        "📊 <b>Kunlik hisobot — {date}</b>\n"
        "👨‍🔧 {name}\n\n"
        "✅ Tayyorlangan buyurtmalar: {orders} ta — <b>{income}</b>\n"
        "📤 Ombordan sotuv: {sold} dona — {sales} (foyda {profit})\n"
        "📥 Sotib olindi: {bought} dona — {buys}\n"
        "📦 Omborda: {units} dona — {value}\n\n"
        "To'liq hisobot PDF faylda 👆",
        "📊 <b>Ежедневный отчёт — {date}</b>\n"
        "👨‍🔧 {name}\n\n"
        "✅ Выполнено заказов: {orders} — <b>{income}</b>\n"
        "📤 Продажи со склада: {sold} шт. — {sales} (прибыль {profit})\n"
        "📥 Куплено: {bought} шт. — {buys}\n"
        "📦 На складе: {units} шт. — {value}\n\n"
        "Полный отчёт — в PDF-файле 👆",
        "📊 <b>Daily report — {date}</b>\n"
        "👨‍🔧 {name}\n\n"
        "✅ Orders completed: {orders} — <b>{income}</b>\n"
        "📤 Stock sales: {sold} pcs — {sales} (profit {profit})\n"
        "📥 Bought: {bought} pcs — {buys}\n"
        "📦 In stock: {units} pcs — {value}\n\n"
        "Full report in the PDF file 👆",
    ),

    # ---------- Admin panel ----------
    "adm_panel": _l(
        "⚙️ <b>ADMIN PANEL</b>\n\nBo'limni tanlang:",
        "⚙️ <b>ADMIN PANEL</b>\n\nВыберите раздел:",
        "⚙️ <b>ADMIN PANEL</b>\n\nChoose a section:",
    ),
    "adm_btn_masters": _l("👨‍🔧 Ustalar", "👨‍🔧 Мастера", "👨‍🔧 Technicians"),
    "adm_btn_stats": _l("📊 Statistika", "📊 Статистика", "📊 Statistics"),
    "adm_btn_income": _l("💰 Daromadlar", "💰 Доходы", "💰 Income"),
    "adm_btn_orders": _l("📦 Buyurtmalar", "📦 Заказы", "📦 Orders"),
    "adm_btn_broadcast": _l("📢 E'lon yuborish", "📢 Отправить объявление", "📢 Send announcement"),
    "adm_btn_backup": _l("💾 Zaxira nusxa (hozir)", "💾 Резервная копия (сейчас)", "💾 Backup (now)"),
    "adm_btn_settings": _l("⚙️ Sozlamalar", "⚙️ Настройки", "⚙️ Settings"),
    "adm_masters": _l(
        "👨‍🔧 <b>USTALAR</b>\n\n"
        "✅ — faol, ⛔️ — bloklangan/tasdiqlanmagan\n"
        "👑 — admin, 🔧 — usta\n\n"
        "Boshqarish uchun ustani tanlang:",
        "👨‍🔧 <b>МАСТЕРА</b>\n\n"
        "✅ — активен, ⛔️ — заблокирован/не подтверждён\n"
        "👑 — админ, 🔧 — мастер\n\n"
        "Выберите мастера для управления:",
        "👨‍🔧 <b>TECHNICIANS</b>\n\n"
        "✅ — active, ⛔️ — blocked/not approved\n"
        "👑 — admin, 🔧 — technician\n\n"
        "Choose a technician to manage:",
    ),
    "adm_master_card": _l(
        "👤 <b>{name}</b>\n\n"
        "Holati: {status}\nRol: {role}\nTil: {language}\n"
        "Username: @{username}\nTelegram ID: <code>{tg_id}</code>\nQo'shilgan: {created}",
        "👤 <b>{name}</b>\n\n"
        "Статус: {status}\nРоль: {role}\nЯзык: {language}\n"
        "Username: @{username}\nTelegram ID: <code>{tg_id}</code>\nДобавлен: {created}",
        "👤 <b>{name}</b>\n\n"
        "Status: {status}\nRole: {role}\nLanguage: {language}\n"
        "Username: @{username}\nTelegram ID: <code>{tg_id}</code>\nJoined: {created}",
    ),
    "adm_active": _l("✅ Faol", "✅ Активен", "✅ Active"),
    "adm_inactive": _l("⛔️ Nofaol", "⛔️ Неактивен", "⛔️ Inactive"),
    "adm_btn_block": _l("⛔️ Bloklash", "⛔️ Заблокировать", "⛔️ Block"),
    "adm_btn_activate": _l("✅ Faollashtirish", "✅ Активировать", "✅ Activate"),
    "adm_btn_delete": _l("🗑 O'chirish", "🗑 Удалить", "🗑 Delete"),
    "adm_btn_approve": _l("✅ Tasdiqlash", "✅ Подтвердить", "✅ Approve"),
    "adm_btn_reject": _l("❌ Rad etish", "❌ Отклонить", "❌ Reject"),
    "adm_not_found": _l("Usta topilmadi.", "Мастер не найден.", "Technician not found."),
    "adm_activated": _l(
        "✅ <b>{name}</b> faollashtirildi.",
        "✅ <b>{name}</b> активирован.",
        "✅ <b>{name}</b> has been activated.",
    ),
    "adm_blocked": _l(
        "⛔️ <b>{name}</b> bloklandi.",
        "⛔️ <b>{name}</b> заблокирован.",
        "⛔️ <b>{name}</b> has been blocked.",
    ),
    "adm_deleted": _l(
        "🗑 <b>{name}</b> tizimdan o'chirildi.",
        "🗑 <b>{name}</b> удалён из системы.",
        "🗑 <b>{name}</b> was removed from the system.",
    ),
    "adm_self_block": _l("O'zingizni bloklay olmaysiz.", "Нельзя заблокировать себя.", "You cannot block yourself."),
    "adm_self_delete": _l("O'zingizni o'chira olmaysiz.", "Нельзя удалить себя.", "You cannot delete yourself."),
    "adm_delete_failed": _l(
        "O'chirib bo'lmadi — bu ustaga bog'langan buyurtmalar bor. Buning o'rniga bloklang.",
        "Не удалось удалить — у мастера есть связанные заказы. Заблокируйте его вместо этого.",
        "Could not delete — this technician has linked orders. Block them instead.",
    ),
    "adm_new_master": _l(
        "🆕 <b>Yangi usta ro'yxatdan o'tdi</b>\n\n"
        "👤 Ism: <b>{name}</b>\n🌐 Til: {language}\n"
        "🆔 Telegram ID: <code>{tg_id}</code>\n👤 Username: @{username}\n\nTasdiqlaysizmi?",
        "🆕 <b>Зарегистрировался новый мастер</b>\n\n"
        "👤 Имя: <b>{name}</b>\n🌐 Язык: {language}\n"
        "🆔 Telegram ID: <code>{tg_id}</code>\n👤 Username: @{username}\n\nПодтвердить?",
        "🆕 <b>A new technician has registered</b>\n\n"
        "👤 Name: <b>{name}</b>\n🌐 Language: {language}\n"
        "🆔 Telegram ID: <code>{tg_id}</code>\n👤 Username: @{username}\n\nApprove?",
    ),
    "adm_stats": _l(
        "📊 <b>STATISTIKA</b>\n\n"
        "📦 Jami buyurtmalar: <b>{total}</b>\n⏳ Kutayotganlar: <b>{pending}</b>\n"
        "✅ Tayyorlar: <b>{ready}</b>\n👨‍🔧 Faol xodimlar: <b>{users}</b>\n"
        "💰 Jami tushum: <b>{revenue}</b>",
        "📊 <b>СТАТИСТИКА</b>\n\n"
        "📦 Всего заказов: <b>{total}</b>\n⏳ В ожидании: <b>{pending}</b>\n"
        "✅ Готовых: <b>{ready}</b>\n👨‍🔧 Активных сотрудников: <b>{users}</b>\n"
        "💰 Общая выручка: <b>{revenue}</b>",
        "📊 <b>STATISTICS</b>\n\n"
        "📦 Total orders: <b>{total}</b>\n⏳ Pending: <b>{pending}</b>\n"
        "✅ Ready: <b>{ready}</b>\n👨‍🔧 Active staff: <b>{users}</b>\n"
        "💰 Total revenue: <b>{revenue}</b>",
    ),
    "adm_stats_per_master": _l("👨‍🔧 <b>Ustalar kesimida:</b>", "👨‍🔧 <b>По мастерам:</b>", "👨‍🔧 <b>By technician:</b>"),
    "adm_stats_row": _l(
        "<b>{name}</b>\nQabul qilgan: {created}\nTayyorlagan: {completed}",
        "<b>{name}</b>\nПринял: {created}\nВыполнил: {completed}",
        "<b>{name}</b>\nAccepted: {created}\nCompleted: {completed}",
    ),
    "adm_income_title": _l("💰 <b>DAROMADLAR</b> — {period}", "💰 <b>ДОХОДЫ</b> — {period}", "💰 <b>INCOME</b> — {period}"),
    "adm_income_row": _l(
        "{i}. <b>{name}</b> — {total} ({count} ta)",
        "{i}. <b>{name}</b> — {total} ({count} шт.)",
        "{i}. <b>{name}</b> — {total} ({count})",
    ),
    "adm_income_total": _l("Jami: <b>{total}</b> ({count} ta)", "Итого: <b>{total}</b> ({count} шт.)", "Total: <b>{total}</b> ({count})"),
    "adm_income_none": _l(
        "Bu davrda tayyor buyurtmalar yo'q.",
        "За этот период готовых заказов нет.",
        "No completed orders in this period.",
    ),
    "adm_orders": _l("📦 <b>BUYURTMALAR</b>", "📦 <b>ЗАКАЗЫ</b>", "📦 <b>ORDERS</b>"),
    "adm_orders_pending": _l("⏳ <b>Kutayotganlar:</b>", "⏳ <b>В ожидании:</b>", "⏳ <b>Pending:</b>"),
    "adm_orders_ready": _l("✅ <b>Oxirgi tayyorlar:</b>", "✅ <b>Последние готовые:</b>", "✅ <b>Recently ready:</b>"),
    "adm_none": _l("yo'q", "нет", "none"),
    "adm_orders_hint": _l(
        "Batafsil ko'rish: 🔎 Buyurtmani topish",
        "Подробнее: 🔎 Найти заказ",
        "Details: 🔎 Find order",
    ),
    "adm_settings": _l(
        "⚙️ <b>SOZLAMALAR</b>\n\n"
        "Guruh ID: {group}\nKutayotganlar topic: {pending}\nTayyorlar topic: {ready}\n"
        "Biz haqimizda topic: {about}\nSavol-javob topic: {faq}\nE'lonlar topic: {elon}\n\n"
        "🖥 Nomi: {wname}\n📞 Telefon: {wphone}\n📍 Manzil: {waddr}\n🕐 Ish vaqti: {whours}\n\n"
        "📊 Kunlik hisobot: har kuni {report}\n💾 Zaxira nusxa: har kuni {backup}\n"
        "⏰ Qolgan ishlar eslatmasi: {reminder}\n\n"
        "Qiymatlar <code>.env</code> fayli orqali o'zgartiriladi (eslatma — pastdagi tugma orqali).\n"
        "ID olish: guruhda /groupid, kerakli topic ichida /topicid\n"
        "«Biz haqimizda» e'lonini yuborish: /post_about",
        "⚙️ <b>НАСТРОЙКИ</b>\n\n"
        "ID группы: {group}\nТопик ожидания: {pending}\nТопик готовых: {ready}\n"
        "Топик «О нас»: {about}\nТопик вопросов: {faq}\nТопик объявлений: {elon}\n\n"
        "🖥 Название: {wname}\n📞 Телефон: {wphone}\n📍 Адрес: {waddr}\n🕐 Часы работы: {whours}\n\n"
        "📊 Ежедневный отчёт: каждый день в {report}\n💾 Резервная копия: каждый день в {backup}\n"
        "⏰ Напоминание о работах: {reminder}\n\n"
        "Значения меняются через файл <code>.env</code> (напоминание — кнопкой ниже).\n"
        "Получить ID: в группе /groupid, внутри топика /topicid\n"
        "Отправить «О нас»: /post_about",
        "⚙️ <b>SETTINGS</b>\n\n"
        "Group ID: {group}\nPending topic: {pending}\nReady topic: {ready}\n"
        "About topic: {about}\nQ&A topic: {faq}\nAnnouncements topic: {elon}\n\n"
        "🖥 Name: {wname}\n📞 Phone: {wphone}\n📍 Address: {waddr}\n🕐 Hours: {whours}\n\n"
        "📊 Daily report: every day at {report}\n💾 Backup: every day at {backup}\n"
        "⏰ Open jobs reminder: {reminder}\n\n"
        "Values are changed in the <code>.env</code> file (the reminder — with the button below).\n"
        "Get IDs: /groupid in the group, /topicid inside a topic\n"
        "Post the «About us» message: /post_about",
    ),
    "adm_not_set": _l("❌ sozlanmagan", "❌ не настроено", "❌ not set"),
    "admin_only": _l(
        "❌ Bu bo'lim faqat adminlar uchun.",
        "❌ Этот раздел только для администраторов.",
        "❌ This section is for administrators only.",
    ),

    # ---------- Qolgan ishlar eslatmasi ----------
    "rem_header": _l(
        "⏰ <b>QOLGAN ISHLAR — {date}</b>\n"
        "📋 Kutayotgan buyurtmalar: <b>{total}</b> ta · ⚠️ {days}+ kun kutayotgani: <b>{overdue}</b> ta\n"
        "<i>eng uzoq kutayotgani birinchi</i>",
        "⏰ <b>НЕЗАВЕРШЁННЫЕ РАБОТЫ — {date}</b>\n"
        "📋 Заказов в ожидании: <b>{total}</b> · ⚠️ ждут {days}+ дн.: <b>{overdue}</b>\n"
        "<i>дольше всех ожидающий — первым</i>",
        "⏰ <b>OPEN JOBS — {date}</b>\n"
        "📋 Pending orders: <b>{total}</b> · ⚠️ waiting {days}+ days: <b>{overdue}</b>\n"
        "<i>longest waiting first</i>",
    ),
    "rem_row": _l(
        "{icon} <b>#{n}</b> · {age}\n📅 {when} · 👤 {customer}\n🔧 {task}\n👨‍🔧 {master}",
        "{icon} <b>#{n}</b> · {age}\n📅 {when} · 👤 {customer}\n🔧 {task}\n👨‍🔧 {master}",
        "{icon} <b>#{n}</b> · {age}\n📅 {when} · 👤 {customer}\n🔧 {task}\n👨‍🔧 {master}",
    ),
    "rem_today": _l("bugun olingan", "принят сегодня", "received today"),
    "rem_days": _l("{n} kundan beri kutmoqda", "ждёт {n} дн.", "waiting {n} days"),
    "rem_footer": _l(
        "⚠️ — kechikkan buyurtmalar. Tayyor bo'lganlarini «🛠 Buyurtmani tayyor qilish» "
        "orqali yoping.",
        "⚠️ — просроченные заказы. Готовые закройте через «🛠 Заказ готов».",
        "⚠️ — overdue orders. Close finished ones with «🛠 Complete order».",
    ),
    "rem_none": _l(
        "✅ <b>{date}</b>: qolgan ish yo'q — barcha buyurtmalar tayyor. Barakalla!",
        "✅ <b>{date}</b>: незавершённых работ нет — все заказы готовы. Отлично!",
        "✅ <b>{date}</b>: no open jobs — every order is done. Great work!",
    ),
    "adm_btn_reminder": _l(
        "⏰ Qolgan ishlar eslatmasi", "⏰ Напоминание о работах", "⏰ Open jobs reminder"
    ),
    "rem_settings": _l(
        "⏰ <b>QOLGAN ISHLAR ESLATMASI</b>\n\n"
        "Har kuni belgilangan vaqtda kutayotgan buyurtmalar ro'yxati — qachon olingani va "
        "necha kundan beri kutayotgani bilan — yuboriladi.\n\n"
        "Holati: {status}\n🕐 Vaqt: <b>{time}</b>\n"
        "⚠️ Kechikkan deb belgilash: <b>{days}</b> kundan keyin\n👥 Kimga: <b>{target}</b>",
        "⏰ <b>НАПОМИНАНИЕ О НЕЗАВЕРШЁННЫХ РАБОТАХ</b>\n\n"
        "Каждый день в указанное время отправляется список заказов в ожидании — когда "
        "принят и сколько дней ждёт.\n\n"
        "Статус: {status}\n🕐 Время: <b>{time}</b>\n"
        "⚠️ Считать просроченным: через <b>{days}</b> дн.\n👥 Кому: <b>{target}</b>",
        "⏰ <b>OPEN JOBS REMINDER</b>\n\n"
        "Every day at the set time, the list of pending orders is sent — when each was "
        "received and how many days it has been waiting.\n\n"
        "Status: {status}\n🕐 Time: <b>{time}</b>\n"
        "⚠️ Mark as overdue after: <b>{days}</b> days\n👥 Recipients: <b>{target}</b>",
    ),
    "rem_on": _l("✅ yoqilgan", "✅ включено", "✅ on"),
    "rem_off": _l("⛔️ o'chirilgan", "⛔️ выключено", "⛔️ off"),
    "rem_target_all": _l("barcha faol ustalar", "все активные мастера", "all active technicians"),
    "rem_target_admins": _l("faqat adminlar", "только администраторы", "admins only"),
    "rem_btn_enable": _l("✅ Yoqish", "✅ Включить", "✅ Turn on"),
    "rem_btn_disable": _l("⛔️ O'chirish", "⛔️ Выключить", "⛔️ Turn off"),
    "rem_btn_time": _l("🕐 Vaqt: {time}", "🕐 Время: {time}", "🕐 Time: {time}"),
    "rem_btn_days": _l(
        "⚠️ Kechikkan: {days} kun", "⚠️ Просрочка: {days} дн.", "⚠️ Overdue: {days} days"
    ),
    "rem_btn_target": _l("👥 Kimga: {target}", "👥 Кому: {target}", "👥 To: {target}"),
    "rem_btn_test": _l(
        "📤 Hozir sinab ko'rish (menga)", "📤 Проверить сейчас (мне)", "📤 Test now (to me)"
    ),
    "rem_btn_custom": _l("✏️ Boshqa vaqt", "✏️ Другое время", "✏️ Other time"),
    "rem_pick_time": _l(
        "🕐 Eslatma vaqtini tanlang (Toshkent vaqti):",
        "🕐 Выберите время напоминания (по Ташкенту):",
        "🕐 Choose the reminder time (Tashkent time):",
    ),
    "rem_pick_days": _l(
        "⚠️ Buyurtma necha kun kutgach «kechikkan» deb belgilansin?",
        "⚠️ Через сколько дней ожидания считать заказ просроченным?",
        "⚠️ After how many days of waiting should an order count as overdue?",
    ),
    "rem_ask_time": _l(
        "✏️ Vaqtni yozing, masalan: <b>19:30</b> yoki <b>8:15</b>",
        "✏️ Напишите время, например: <b>19:30</b> или <b>8:15</b>",
        "✏️ Type the time, for example: <b>19:30</b> or <b>8:15</b>",
    ),
    "rem_bad_time": _l(
        "❌ Vaqt noto'g'ri. Masalan: <b>19:30</b>",
        "❌ Неверное время. Например: <b>19:30</b>",
        "❌ Invalid time. Example: <b>19:30</b>",
    ),
    "rem_saved": _l("✅ Saqlandi", "✅ Сохранено", "✅ Saved"),
    "rem_test_sent": _l(
        "📤 Eslatma sizga yuborildi", "📤 Напоминание отправлено вам", "📤 Reminder sent to you"
    ),

    # ---------- E'lon (broadcast) ----------
    "bc_choose_target": _l(
        "📢 <b>E'LON YUBORISH</b>\n\nE'lon kimga yuborilsin?",
        "📢 <b>ОТПРАВКА ОБЪЯВЛЕНИЯ</b>\n\nКому отправить объявление?",
        "📢 <b>SEND ANNOUNCEMENT</b>\n\nWho should receive it?",
    ),
    "bc_btn_masters": _l("👨‍🔧 Ustalarga (botda)", "👨‍🔧 Мастерам (в боте)", "👨‍🔧 Technicians (in bot)"),
    "bc_btn_group": _l("👥 Ustaxona guruhiga", "👥 В группу мастерской", "👥 Workshop group"),
    "bc_ask_content": _l(
        "✏️ E'lonni yuboring: matn, rasm, video yoki fayl (izoh bilan bo'lishi mumkin).\n\n"
        "Kimga: <b>{target}</b>",
        "✏️ Отправьте объявление: текст, фото, видео или файл (можно с подписью).\n\n"
        "Кому: <b>{target}</b>",
        "✏️ Send the announcement: text, photo, video or file (a caption is fine).\n\n"
        "To: <b>{target}</b>",
    ),
    "bc_target_masters": _l("barcha faol ustalar", "все активные мастера", "all active technicians"),
    "bc_target_group": _l("Ustaxona guruhi (E'lonlar bo'limi)", "группа мастерской (раздел объявлений)", "workshop group (Announcements topic)"),
    "bc_preview": _l(
        "👆 E'lon shunday ko'rinadi.\n\nKimga: <b>{target}</b>\nYuborilsinmi?",
        "👆 Так будет выглядеть объявление.\n\nКому: <b>{target}</b>\nОтправить?",
        "👆 This is how the announcement will look.\n\nTo: <b>{target}</b>\nSend it?",
    ),
    "bc_unsupported": _l(
        "❌ Bu turdagi xabarni yuborib bo'lmaydi. Matn, rasm, video yoki fayl yuboring.",
        "❌ Такой тип сообщения не поддерживается. Отправьте текст, фото, видео или файл.",
        "❌ This message type is not supported. Send text, a photo, a video or a file.",
    ),
    "bc_sending": _l("⏳ Yuborilmoqda…", "⏳ Отправляю…", "⏳ Sending…"),
    "bc_done_masters": _l(
        "✅ E'lon yuborildi: {ok} ta ustaga.{failed}",
        "✅ Объявление отправлено: мастеров — {ok}.{failed}",
        "✅ Announcement sent to {ok} technicians.{failed}",
    ),
    "bc_failed_part": _l(
        "\n⚠️ Yetib bormadi: {n} ta (botni bloklagan bo'lishi mumkin).",
        "\n⚠️ Не доставлено: {n} (возможно, заблокировали бота).",
        "\n⚠️ Not delivered: {n} (they may have blocked the bot).",
    ),
    "bc_done_group": _l(
        "✅ E'lon guruhga joylandi.",
        "✅ Объявление опубликовано в группе.",
        "✅ The announcement was posted to the group.",
    ),
    "bc_group_failed": _l(
        "❌ Guruhga yuborib bo'lmadi: {err}",
        "❌ Не удалось отправить в группу: {err}",
        "❌ Could not post to the group: {err}",
    ),
    "bc_no_group": _l(
        "❌ GROUP_ID sozlanmagan — guruhga yuborib bo'lmaydi.",
        "❌ GROUP_ID не настроен — отправка в группу невозможна.",
        "❌ GROUP_ID is not set — cannot post to the group.",
    ),
    "bc_from_admin": _l(
        "📢 <b>Administrator e'loni</b>",
        "📢 <b>Объявление администратора</b>",
        "📢 <b>Announcement from the administrator</b>",
    ),

    # ---------- Zaxira ----------
    "backup_making": _l(
        "⏳ Zaxira nusxa olinmoqda…",
        "⏳ Создаю резервную копию…",
        "⏳ Creating a backup…",
    ),
    "backup_caption": _l(
        "💾 <b>Ma'lumotlar bazasi zaxirasi</b>\n"
        "🕐 {when}\n"
        "📦 Buyurtmalar: {orders} · Ustalar: {users} · Mahsulotlar: {products}\n\n"
        "Tiklash (serverda, bot papkasida):\n"
        "<code>gunzip -c {file} | docker compose exec -T db psql -U ustaxona -d ustaxona</code>",
        "💾 <b>Резервная копия базы данных</b>\n"
        "🕐 {when}\n"
        "📦 Заказов: {orders} · Мастеров: {users} · Товаров: {products}\n\n"
        "Восстановление (на сервере, в папке бота):\n"
        "<code>gunzip -c {file} | docker compose exec -T db psql -U ustaxona -d ustaxona</code>",
        "💾 <b>Database backup</b>\n"
        "🕐 {when}\n"
        "📦 Orders: {orders} · Staff: {users} · Products: {products}\n\n"
        "Restore (on the server, in the bot folder):\n"
        "<code>gunzip -c {file} | docker compose exec -T db psql -U ustaxona -d ustaxona</code>",
    ),
    "backup_failed": _l(
        "⚠️ <b>Zaxira nusxa olinmadi!</b>\n\n<code>{err}</code>\n\nServerni tekshiring.",
        "⚠️ <b>Резервная копия не создана!</b>\n\n<code>{err}</code>\n\nПроверьте сервер.",
        "⚠️ <b>Backup failed!</b>\n\n<code>{err}</code>\n\nPlease check the server.",
    ),

    # ---------- Yangilanish xabari: Mini App ----------
    "update_announce_app": _l(
        "📱 <b>Yangilik: bot endi ilova ko'rinishida ham ishlaydi!</b>\n\n"
        "Telegram ichida to'liq ilova ochiladi — hammasi bitta ekranda:\n"
        "📋 Buyurtmalar: kutayotgan va tayyorlar, tez qidiruv, mijozga bir bosishda qo'ng'iroq\n"
        "➕ Yangi buyurtma: telefon → ism → vazifa, mijoz bazada bo'lsa ismi o'zi chiqadi\n"
        "✅ Buyurtmani tayyor qilish — kartochkaning o'zidan\n"
        "📦 Ombor: sotib oldim / sotdim, qoldiq va tarix\n"
        "📊 Hisobot: daromad, sotuv, foyda + PDF\n\n"
        "Ochish: pastdagi tugma yoki chatdagi «📱 Ilova» menyu tugmasi.\n"
        "Odatdagi chat menyusi ham avvalgidek ishlayveradi. /start",
        "📱 <b>Новинка: бот теперь работает и как приложение!</b>\n\n"
        "Внутри Telegram открывается полноценное приложение — всё на одном экране:\n"
        "📋 Заказы: в ожидании и готовые, быстрый поиск, звонок клиенту в одно касание\n"
        "➕ Новый заказ: телефон → имя → задача, имя известного клиента подставится само\n"
        "✅ Отметить заказ готовым — прямо из карточки\n"
        "📦 Склад: купил / продал, остатки и история\n"
        "📊 Отчёты: доход, продажи, прибыль + PDF\n\n"
        "Открыть: кнопка ниже или кнопка меню «📱 Ilova» в чате.\n"
        "Обычное меню в чате тоже работает как раньше. /start",
        "📱 <b>New: the bot now works as an app too!</b>\n\n"
        "A full app opens right inside Telegram — everything on one screen:\n"
        "📋 Orders: pending and ready, quick search, call the customer in one tap\n"
        "➕ New order: phone → name → task, known customers are filled in automatically\n"
        "✅ Mark an order as ready — straight from its card\n"
        "📦 Stock: bought / sold, current stock and history\n"
        "📊 Reports: income, sales, profit + PDF\n\n"
        "Open it: the button below or the «📱 Ilova» menu button in the chat.\n"
        "The usual chat menu keeps working as before. /start",
    ),

    # ---------- Yangilanish xabari ----------
    "update_announce": _l(
        "🆕 <b>Bot yangilandi!</b>\n\n"
        "Yangi imkoniyatlar:\n"
        "📞 Yangi buyurtma: avval mijoz raqami (sonli klaviatura bilan), keyin ismi, keyin vazifa\n"
        "📦 «Omborim»: sotib olgan va sotgan mahsulotlaringiz sana-vaqti bilan\n"
        "📊 Har kuni soat {report} da kunlik hisobot (PDF)\n"
        "📄 Kutayotgan va tayyor buyurtmalar bo'yicha PDF hisobot\n"
        "🌐 Bot endi 3 tilda: o'zbek, rus, ingliz\n\n"
        "Tekshirib ko'rish uchun /start buyrug'ini bosing 👉 /start",
        "🆕 <b>Бот обновлён!</b>\n\n"
        "Что нового:\n"
        "📞 Новый заказ: сначала номер клиента (с цифровой клавиатурой), затем имя, затем задача\n"
        "📦 «Мой склад»: купленные и проданные товары с датой и временем\n"
        "📊 Ежедневный отчёт в {report} (PDF)\n"
        "📄 PDF-отчёты по заказам в ожидании и готовым\n"
        "🌐 Бот теперь на 3 языках: узбекский, русский, английский\n\n"
        "Чтобы проверить, нажмите /start 👉 /start",
        "🆕 <b>The bot has been updated!</b>\n\n"
        "What's new:\n"
        "📞 New order: customer phone first (with a numeric keypad), then name, then the task\n"
        "📦 «My stock»: items you bought and sold, with date and time\n"
        "📊 Daily report every day at {report} (PDF)\n"
        "📄 PDF reports for pending and ready orders\n"
        "🌐 The bot now speaks 3 languages: Uzbek, Russian, English\n\n"
        "To check it out, tap /start 👉 /start",
    ),
}


def t(key: str, lang: str, **kwargs) -> str:
    variants = TEXTS[key]
    template = variants.get(lang) or variants["uz"]
    return template.format(**kwargs) if kwargs else template


# Ro'yxatdan o'tmagan / nofaol foydalanuvchiga (tili noma'lum) — 3 tilda.
DENIED_TEXT = (
    "❌ Siz ushbu tizimdan foydalanish huquqiga ega emassiz. "
    "Administrator bilan bog'laning.\n\n"
    "❌ У вас нет доступа к этой системе. Свяжитесь с администратором.\n\n"
    "❌ You do not have access to this system. Please contact the administrator."
)
INACTIVE_TEXT = (
    "⏳ Profilingiz hali administrator tomonidan tasdiqlanmagan. Iltimos, kuting.\n\n"
    "⏳ Ваш профиль ещё не подтверждён администратором. Пожалуйста, подождите.\n\n"
    "⏳ Your profile has not been approved by an administrator yet. Please wait."
)
