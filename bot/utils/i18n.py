"""Usta interfeysi uchun ikki tillik (uz/ru) matnlar.

Guruhga chiqadigan mijoz xabarlari bunga kirmaydi — ular formatters.py da
3 tilda turadi. Bu modul faqat botning usta bilan muloqoti uchun.
"""

LANGS = ("uz", "ru")

# ---------- Tugmalar (reply keyboard) ----------
# Handler'lar ikkala til variantini ham qabul qilishi uchun btn_variants() bor.

BUTTONS = {
    "new_order": {"uz": "➕ Yangi buyurtma", "ru": "➕ Новый заказ"},
    "complete": {"uz": "🛠 Buyurtmani tayyor qilish", "ru": "🛠 Заказ готов"},
    "pending": {"uz": "📋 Kutayotgan buyurtmalar", "ru": "📋 Заказы в ожидании"},
    "ready_list": {"uz": "✅ Tayyor buyurtmalar", "ru": "✅ Готовые заказы"},
    "search": {"uz": "🔎 Buyurtmani topish", "ru": "🔎 Найти заказ"},
    "my_income": {"uz": "💰 Daromadim", "ru": "💰 Мой доход"},
    "profile": {"uz": "👤 Profil", "ru": "👤 Профиль"},
    "admin": {"uz": "⚙️ Admin panel", "ru": "⚙️ Admin panel"},
    "cancel": {"uz": "❌ Bekor qilish", "ru": "❌ Отмена"},
    "confirm_accept": {"uz": "✅ Qabul qilindi", "ru": "✅ Принять"},
    "confirm_ready": {"uz": "✅ TAYYOR", "ru": "✅ ГОТОВО"},
}


def btn(key: str, lang: str) -> str:
    variants = BUTTONS[key]
    return variants.get(lang, variants["uz"])


def btn_variants(key: str) -> set[str]:
    return set(BUTTONS[key].values())


# ---------- Matnlar ----------

TEXTS = {
    # Til tanlash / registratsiya
    "choose_language": {
        "uz": "🌐 Tilni tanlang / Выберите язык:",
        "ru": "🌐 Tilni tanlang / Выберите язык:",
    },
    "lang_set": {"uz": "✅ Til: O'zbekcha 🇺🇿", "ru": "✅ Язык: Русский 🇷🇺"},
    "reg_ask_name": {
        "uz": (
            "Assalomu alaykum!\n\n"
            "Kompyuter servis boshqaruv botiga xush kelibsiz.\n\n"
            "Avval tizimda ro'yxatdan o'tishingiz kerak.\n\n"
            "Iltimos, ismingizni kiriting:"
        ),
        "ru": (
            "Здравствуйте!\n\n"
            "Добро пожаловать в бот управления компьютерным сервисом.\n\n"
            "Сначала нужно зарегистрироваться.\n\n"
            "Пожалуйста, введите ваше имя:"
        ),
    },
    "reg_name_invalid": {
        "uz": "❌ Ism 2 tadan 50 tagacha belgidan iborat bo'lishi kerak.\nQayta kiriting:",
        "ru": "❌ Имя должно содержать от 2 до 50 символов.\nВведите ещё раз:",
    },
    "reg_already": {
        "uz": "Siz allaqachon ro'yxatdan o'tgansiz.",
        "ru": "Вы уже зарегистрированы.",
    },
    "reg_wait_approval": {
        "uz": (
            "✅ Rahmat, <b>{name}</b>!\n\n"
            "Ma'lumotlaringiz qabul qilindi.\n"
            "⏳ Administrator profilingizni tasdiqlagach, sizga xabar beramiz."
        ),
        "ru": (
            "✅ Спасибо, <b>{name}</b>!\n\n"
            "Ваши данные приняты.\n"
            "⏳ Как только администратор подтвердит ваш профиль, мы сообщим вам."
        ),
    },
    "reg_admin_welcome": {
        "uz": (
            "✅ Xush kelibsiz, <b>{name}</b>!\n\n"
            "Siz <b>administrator</b> sifatida ro'yxatdan o'tdingiz."
        ),
        "ru": (
            "✅ Добро пожаловать, <b>{name}</b>!\n\n"
            "Вы зарегистрированы как <b>администратор</b>."
        ),
    },
    "welcome_back": {
        "uz": "Xush kelibsiz, <b>{name}</b>! 👋",
        "ru": "С возвращением, <b>{name}</b>! 👋",
    },
    "pending_approval": {
        "uz": (
            "⏳ Profilingiz administrator tasdig'ini kutmoqda.\n"
            "Tasdiqlangach sizga xabar beramiz."
        ),
        "ru": (
            "⏳ Ваш профиль ожидает подтверждения администратора.\n"
            "Мы сообщим вам после подтверждения."
        ),
    },
    "approved_notice": {
        "uz": (
            "🎉 Profilingiz administrator tomonidan tasdiqlandi!\n\n"
            "Endi tizimdan to'liq foydalanishingiz mumkin."
        ),
        "ru": (
            "🎉 Ваш профиль подтверждён администратором!\n\n"
            "Теперь вы можете полноценно пользоваться системой."
        ),
    },
    "blocked_notice": {
        "uz": "⛔️ Profilingiz administrator tomonidan bloklandi.",
        "ru": "⛔️ Ваш профиль заблокирован администратором.",
    },

    # Umumiy
    "cancelled": {"uz": "❌ Amal bekor qilindi.", "ru": "❌ Действие отменено."},
    "use_menu": {
        "uz": "Quyidagi menyudan foydalaning 👇",
        "ru": "Используйте меню ниже 👇",
    },
    "continue": {"uz": "Davom etamiz 👇", "ru": "Продолжаем 👇"},
    "fsm_hint": {
        "uz": (
            "Iltimos, so'ralgan ma'lumotni matn ko'rinishida yuboring "
            "yoki «❌ Bekor qilish» tugmasini bosing."
        ),
        "ru": (
            "Пожалуйста, отправьте запрошенные данные текстом "
            "или нажмите «❌ Отмена»."
        ),
    },
    "menu_placeholder": {"uz": "Amalni tanlang…", "ru": "Выберите действие…"},

    # Yangi buyurtma oqimi
    "ask_customer_name": {
        "uz": "📥 <b>Yangi buyurtma</b>\n\n👤 Mijoz ismini kiriting:",
        "ru": "📥 <b>Новый заказ</b>\n\n👤 Введите имя клиента:",
    },
    "invalid_customer_name": {
        "uz": "❌ Ism 2 tadan 50 tagacha belgidan iborat bo'lishi kerak.\nQayta kiriting:",
        "ru": "❌ Имя должно содержать от 2 до 50 символов.\nВведите ещё раз:",
    },
    "ask_customer_phone": {
        "uz": "📞 Mijoz telefon raqamini kiriting:\n\nMasalan: <b>+998901234567</b>",
        "ru": "📞 Введите номер телефона клиента:\n\nНапример: <b>+998901234567</b>",
    },
    "invalid_phone": {
        "uz": (
            "❌ Telefon raqami noto'g'ri.\n"
            "Faqat raqamlar (va boshida +) bo'lsin.\n\n"
            "Masalan: <b>+998901234567</b>"
        ),
        "ru": (
            "❌ Неверный номер телефона.\n"
            "Только цифры (и + в начале).\n\n"
            "Например: <b>+998901234567</b>"
        ),
    },
    "ask_description": {
        "uz": "🔧 Nima qilish kerak?\n\nMuammo/vazifani qisqacha yozing:",
        "ru": "🔧 Что нужно сделать?\n\nКоротко опишите проблему/задачу:",
    },
    "invalid_description": {
        "uz": "❌ Tavsif juda qisqa yoki juda uzun (3–500 belgi). Qayta yozing:",
        "ru": "❌ Описание слишком короткое или длинное (3–500 символов). Напишите ещё раз:",
    },
    "order_summary": {
        "uz": (
            "🧾 <b>YANGI BUYURTMA</b>\n\n"
            "🔢 Buyurtma raqami: <b>#{n}</b> (avtomatik)\n"
            "👤 Mijoz: <b>{name}</b>\n"
            "📞 Telefon: <b>{phone}</b>\n"
            "🔧 Vazifa: {task}\n\n"
            "Buyurtma qabul qilinsinmi?"
        ),
        "ru": (
            "🧾 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
            "🔢 Номер заказа: <b>#{n}</b> (автоматически)\n"
            "👤 Клиент: <b>{name}</b>\n"
            "📞 Телефон: <b>{phone}</b>\n"
            "🔧 Задача: {task}\n\n"
            "Принять заказ?"
        ),
    },
    "order_created": {
        "uz": "✅ Buyurtma <b>#{n}</b> qabul qilindi!\n\n{note}",
        "ru": "✅ Заказ <b>#{n}</b> принят!\n\n{note}",
    },
    "group_sent_pending": {
        "uz": "📤 Guruhdagi «Kutayotgan buyurtmalar» bo'limiga e'lon yuborildi.",
        "ru": "📤 Объявление отправлено в раздел «Kutayotganlar» группы.",
    },
    "group_send_failed": {
        "uz": (
            "⚠️ Guruhga e'lon yuborib bo'lmadi (sozlamalarni tekshiring). "
            "Buyurtma bazaga saqlandi."
        ),
        "ru": (
            "⚠️ Не удалось отправить объявление в группу (проверьте настройки). "
            "Заказ сохранён в базе."
        ),
    },
    "order_create_cancelled": {
        "uz": "❌ Buyurtma yaratish bekor qilindi.",
        "ru": "❌ Создание заказа отменено.",
    },

    # Buyurtmani tayyor qilish oqimi
    "ask_ready_number": {
        "uz": "🔢 Tayyor bo'lgan buyurtma raqamini kiriting:",
        "ru": "🔢 Введите номер готового заказа:",
    },
    "invalid_number": {
        "uz": "❌ Buyurtma raqami faqat raqamlardan iborat bo'lishi kerak.\n\nMasalan: <b>27</b>",
        "ru": "❌ Номер заказа должен состоять только из цифр.\n\nНапример: <b>27</b>",
    },
    "order_not_found": {
        "uz": (
            "❌ <b>#{n}</b> raqamli buyurtma topilmadi.\n\n"
            "Raqamni tekshirib qayta kiriting."
        ),
        "ru": (
            "❌ Заказ <b>#{n}</b> не найден.\n\n"
            "Проверьте номер и введите ещё раз."
        ),
    },
    "already_ready": {
        "uz": "ℹ️ <b>#{n}</b> raqamli buyurtma allaqachon tayyor deb belgilangan.",
        "ru": "ℹ️ Заказ <b>#{n}</b> уже отмечен как готовый.",
    },
    "was_cancelled": {
        "uz": "ℹ️ <b>#{n}</b> raqamli buyurtma bekor qilingan.",
        "ru": "ℹ️ Заказ <b>#{n}</b> был отменён.",
    },
    "ask_work_done": {
        "uz": (
            "🔧 <b>Buyurtma #{n}</b>\n\n"
            "Qanday ishlar bajarildi?\n\n"
            "Bajarilgan ishlarni batafsil yozing (har birini yangi qatordan):"
        ),
        "ru": (
            "🔧 <b>Заказ #{n}</b>\n\n"
            "Какие работы выполнены?\n\n"
            "Опишите выполненные работы подробно (каждую с новой строки):"
        ),
    },
    "work_too_short": {
        "uz": "❌ Bajarilgan ishlar tavsifi juda qisqa. Batafsilroq yozing:",
        "ru": "❌ Описание работ слишком короткое. Напишите подробнее:",
    },
    "work_too_long": {
        "uz": "❌ Tavsif juda uzun (maksimum 2000 belgi). Qisqartiring:",
        "ru": "❌ Описание слишком длинное (максимум 2000 символов). Сократите:",
    },
    "ask_price": {
        "uz": "💰 Xizmat haqqini kiriting:\n\nMasalan:\n<b>250000</b>",
        "ru": "💰 Введите стоимость услуги:\n\nНапример:\n<b>250000</b>",
    },
    "invalid_price": {
        "uz": "❌ Iltimos, summani faqat raqam bilan kiriting.\n\nMasalan:\n<b>250000</b>",
        "ru": "❌ Пожалуйста, введите сумму только цифрами.\n\nНапример:\n<b>250000</b>",
    },
    "ready_summary": {
        "uz": (
            "📋 <b>Buyurtma #{n}</b>\n\n"
            "🔧 <b>Bajarilgan ishlar:</b>\n{work}\n\n"
            "💰 Xizmat haqqi: <b>{price}</b>\n\n"
            "Buyurtma tayyormi?"
        ),
        "ru": (
            "📋 <b>Заказ #{n}</b>\n\n"
            "🔧 <b>Выполненные работы:</b>\n{work}\n\n"
            "💰 Стоимость: <b>{price}</b>\n\n"
            "Заказ готов?"
        ),
    },
    "ready_done": {
        "uz": "✅ Buyurtma <b>#{n}</b> tayyor deb belgilandi!\n\n{note}",
        "ru": "✅ Заказ <b>#{n}</b> отмечен как готовый!\n\n{note}",
    },
    "group_sent_ready": {
        "uz": "📤 Guruhdagi «Tayyor buyurtmalar» bo'limiga e'lon yuborildi.",
        "ru": "📤 Объявление отправлено в раздел «Tayyorlar» группы.",
    },
    "group_send_failed_ready": {
        "uz": (
            "⚠️ Guruhga e'lon yuborib bo'lmadi (sozlamalarni tekshiring). "
            "Buyurtma bazada TAYYOR deb belgilandi."
        ),
        "ru": (
            "⚠️ Не удалось отправить объявление в группу (проверьте настройки). "
            "Заказ отмечен как ГОТОВЫЙ в базе."
        ),
    },
    "complete_cancelled": {
        "uz": "❌ Amal bekor qilindi. Buyurtma o'zgartirilmadi.",
        "ru": "❌ Действие отменено. Заказ не изменён.",
    },
    "order_vanished": {
        "uz": "❌ Buyurtma topilmadi. Qaytadan urinib ko'ring.",
        "ru": "❌ Заказ не найден. Попробуйте ещё раз.",
    },

    # Qidiruv va ro'yxatlar
    "search_prompt": {
        "uz": "🔎 Buyurtma raqamini kiriting:",
        "ru": "🔎 Введите номер заказа:",
    },
    "search_not_found": {
        "uz": "❌ <b>#{n}</b> raqamli buyurtma topilmadi.\n\nBoshqa raqam kiriting yoki bekor qiling.",
        "ru": "❌ Заказ <b>#{n}</b> не найден.\n\nВведите другой номер или отмените.",
    },
    "pending_header": {
        "uz": "📋 <b>KUTAYOTGAN BUYURTMALAR</b>\n",
        "ru": "📋 <b>ЗАКАЗЫ В ОЖИДАНИИ</b>\n",
    },
    "ready_header": {
        "uz": "✅ <b>TAYYOR BUYURTMALAR</b> (oxirgi 10 ta)\n",
        "ru": "✅ <b>ГОТОВЫЕ ЗАКАЗЫ</b> (последние 10)\n",
    },
    "none_pending": {
        "uz": "📋 Hozircha kutayotgan buyurtmalar yo'q.",
        "ru": "📋 Пока нет заказов в ожидании.",
    },
    "none_ready": {
        "uz": "✅ Hozircha tayyor buyurtmalar yo'q.",
        "ru": "✅ Пока нет готовых заказов.",
    },

    # Profil
    "profile_card": {
        "uz": (
            "👤 <b>PROFIL</b>\n\n"
            "Ism: <b>{name}</b>\n"
            "Rol: {role}\n"
            "Til: O'zbekcha 🇺🇿\n"
            "Telegram ID: <code>{tg_id}</code>\n"
            "Ro'yxatdan o'tgan: {created}"
        ),
        "ru": (
            "👤 <b>ПРОФИЛЬ</b>\n\n"
            "Имя: <b>{name}</b>\n"
            "Роль: {role}\n"
            "Язык: Русский 🇷🇺\n"
            "Telegram ID: <code>{tg_id}</code>\n"
            "Зарегистрирован: {created}"
        ),
    },
    "role_admin": {"uz": "👑 Administrator", "ru": "👑 Администратор"},
    "role_master": {"uz": "🔧 Usta", "ru": "🔧 Мастер"},

    # Daromad hisoboti
    "income_header": {
        "uz": "💰 <b>DAROMADIM</b>\n👨‍🔧 {name}\n",
        "ru": "💰 <b>МОЙ ДОХОД</b>\n👨‍🔧 {name}\n",
    },
    "income_row": {
        "uz": "{icon} {label}: <b>{total}</b> — {count} ta buyurtma",
        "ru": "{icon} {label}: <b>{total}</b> — заказов: {count}",
    },
    "period_today": {"uz": "Bugun", "ru": "Сегодня"},
    "period_week": {"uz": "Shu hafta", "ru": "Эта неделя"},
    "period_month": {"uz": "Shu oy", "ru": "Этот месяц"},
    "period_all": {"uz": "Jami (hozirgacha)", "ru": "Всего (за всё время)"},
}


def t(key: str, lang: str, **kwargs) -> str:
    variants = TEXTS[key]
    template = variants.get(lang) or variants["uz"]
    return template.format(**kwargs) if kwargs else template
