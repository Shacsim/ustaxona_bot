# 🖥 Ustaxona Bot — Kompyuter Servisi uchun Telegram boshqaruv tizimi

Kompyuter ta'mirlash ustaxonasi uchun buyurtmalarni boshqarish tizimi:

- **Telegram Bot** — ustalar/adminlar buyurtmalarni qabul qiladi va tayyor deb belgilaydi;
- **Telegram Supergroup (Forum)** — mijozlar buyurtma holatini va ustaxona ma'lumotlarini ko'radi.

## Texnologiyalar

Python 3.11+ · aiogram 3.x · PostgreSQL · SQLAlchemy 2.x (async) · Alembic · Docker Compose

## Arxitektura

```text
ustaxona_bot/
├── bot/
│   ├── handlers/        # registratsiya, menyu, buyurtma oqimlari, admin, guruh
│   ├── keyboards/       # reply va inline klaviaturalar
│   ├── middlewares/     # DB sessiya, user yuklash, authorization
│   ├── services/        # guruhga e'lon yuborish (group_publisher)
│   ├── states/          # FSM holatlari
│   └── utils/           # formatlash va validatsiya
├── database/
│   ├── models/          # users, orders
│   ├── repositories/    # barcha SQL shu yerda
│   └── migrations/      # Alembic
├── config/              # .env dan o'qiladigan sozlamalar
├── main.py
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

**Xavfsizlik modeli:**

- `ADMIN_IDS` dagi Telegram ID'lar ro'yxatdan o'tishi bilan **faol admin** bo'ladi.
- Boshqa yangi ustalar ro'yxatdan o'tadi, lekin **admin tasdiqlaguncha nofaol** —
  adminlarga tasdiqlash tugmali xabar boradi.
- Ro'yxatda yo'q/bloklangan foydalanuvchi botdan foydalana olmaydi.
- Guruhda himoyalangan topic'larga begona yozsa, bot xabarini o'chiradi
  (asosiy himoya — Telegram permissionlari, bot qo'shimcha qatlam).

---

## 1. O'rnatish (lokal)

### 1.1. Python 3.11+ borligini tekshiring

```bash
python3 --version
```

### 1.2. Virtual environment

```bash
cd ustaxona_bot
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 1.3. Kutubxonalar

```bash
pip install -r requirements.txt
```

### 1.4. PostgreSQL

macOS (Homebrew):

```bash
brew install postgresql@16
brew services start postgresql@16
createdb ustaxona
psql ustaxona -c "CREATE USER ustaxona WITH PASSWORD 'ustaxona'; GRANT ALL PRIVILEGES ON DATABASE ustaxona TO ustaxona; ALTER DATABASE ustaxona OWNER TO ustaxona;"
```

Yoki faqat Postgres'ni Docker'da ko'taring:

```bash
docker compose up -d db
```

### 1.5. `.env` sozlash

```bash
cp .env.example .env
```

`.env` ni oching va to'ldiring:

| O'zgaruvchi | Qayerdan olinadi |
|---|---|
| `BOT_TOKEN` | @BotFather → `/newbot` |
| `DATABASE_URL` | lokal Postgres bo'lsa tayyor qiymat ishlaydi |
| `ADMIN_IDS` | o'z Telegram ID'ingiz (@userinfobot ga yozing) |
| `GROUP_ID`, `*_TOPIC_ID` | quyidagi 3-bo'limga qarang (keyinroq to'ldiriladi) |
| `WORKSHOP_*` | ustaxona telefoni, manzili, ish vaqti, koordinatalari |

### 1.6. Migratsiya

```bash
alembic upgrade head
```

### 1.7. Botni ishga tushirish

```bash
python main.py
```

---

## 2. Docker orqali ishga tushirish

`.env` ni to'ldirgach (DATABASE_URL ni o'zgartirish shart emas — compose o'zi to'g'irlaydi):

```bash
docker compose up -d --build
docker compose logs -f bot     # loglarni kuzatish
```

Migratsiyalar konteyner ichida avtomatik bajariladi (`alembic upgrade head`).

---

## 3. Telegram guruh va topic'larni sozlash

### 3.1. Bot yaratish

1. @BotFather → `/newbot` → nom va username bering.
2. Tokenni `.env` dagi `BOT_TOKEN` ga yozing.
3. `/setprivacy` → botingizni tanlang → **Disable** qiling
   (guruhdagi buyruqlar va qo'riqchi ishlashi uchun bot xabarlarni ko'rishi kerak).

### 3.2. Guruh yaratish

1. Yangi **guruh** yarating (masalan: «Kompyuter Servisi»).
2. Guruh sozlamalari → **Chat history for new members** → *Visible*
   (mijozlar eski e'lonlarni ko'rishi uchun).
3. Guruh sozlamalari → **Topics** ni yoqing — guruh forum rejimiga o'tadi.

### 3.3. Botni guruhga qo'shish

1. Botni guruhga qo'shing.
2. Botni **administrator** qiling, quyidagi huquqlar bilan:
   - ✅ Manage topics
   - ✅ Delete messages
   - ✅ Pin messages

### 3.4. Topic'lar yaratish

Guruhda qo'lda 4 ta topic yarating:

```text
📋 KUTAYOTGAN BUYURTMALAR
✅ TAYYOR BUYURTMALAR
🏢 BIZ HAQIMIZDA
❓ SAVOL-JAVOBLAR
```

(Kelajakda istalgancha yangi topic qo'shishingiz mumkin — tizimga faqat
shu 4 tasining ID'si kerak.)

### 3.5. ID'larni olish va `.env` ga yozish

1. Guruhning istalgan joyida: `/groupid` → chiqqan qiymatni `GROUP_ID` ga yozing.
2. Har bir topic **ichida**: `/topicid` → qiymatlarni mos ravishda
   `PENDING_TOPIC_ID`, `READY_TOPIC_ID`, `ABOUT_TOPIC_ID`, `FAQ_TOPIC_ID` ga yozing.
3. Botni qayta ishga tushiring (`python main.py` yoki `docker compose restart bot`).

### 3.6. Yozish huquqlarini sozlash (muhim!)

Mijozlar faqat «Savol-javoblar»da yozsin:

1. Guruh sozlamalari → **Permissions** → *Send messages* — **ON** qoldiring
   (aks holda Savol-javobda ham yozolmaydilar).
2. Guruhda (admin sifatida) quyidagi buyruqni yozing:

   ```text
   /close_topics
   ```

   Bot 3 ta himoyalangan topic'ni (Kutayotganlar, Tayyorlar, Biz haqimizda)
   o'zi yopadi. Yopiq topic'ga faqat adminlar (va bot) yoza oladi —
   mijozlar yozolmaydi. (Topic ID'lar .env da sozlangan bo'lishi kerak.)
3. ❓ SAVOL-JAVOBLAR ochiq qoladi — mijozlar shu yerda savol beradi.
4. Xohlasangiz **General** topic'ni yashiring (guruh sozlamalari → Manage topics → Hide General).

Bot qo'shimcha qo'riqchi vazifasini ham bajaradi: himoyalangan topic'larga
tizimda ro'yxatdan o'tmagan odam yozsa, xabari avtomatik o'chiriladi.

### 3.7. «Biz haqimizda» ma'lumotini joylash

Guruhda (admin sifatida):

```text
/post_about
```

Bot `.env` dagi telefon, manzil, ish vaqti va lokatsiyani
🏢 BIZ HAQIMIZDA topic'iga yuboradi. Xohlasangiz xabarni pin qiling.

---

## 4. Foydalanish oqimi

### Usta ro'yxatdan o'tishi

1. Usta botga `/start` yozadi → ismini kiritadi.
2. `ADMIN_IDS` dagi foydalanuvchi darhol faol admin bo'ladi.
3. Boshqa ustalarga admin tasdig'i kerak — adminlarga tugmali xabar boradi.

### Buyurtma qabul qilish

```text
➕ Yangi buyurtma → raqam (bot keyingisini taklif qiladi) → ✅ Qabul qilindi
→ guruhdagi 📋 KUTAYOTGAN BUYURTMALAR ga chiroyli e'lon (usta ismi bilan)
```

Buyurtma raqamini mijozga bering — u guruhda o'z raqamini kuzatadi.

### Buyurtmani tayyor qilish

```text
🛠 Buyurtmani tayyor qilish → raqam → bajarilgan ishlar → xizmat haqqi
→ ✅ TAYYOR → guruhdagi ✅ TAYYOR BUYURTMALAR ga e'lon
→ eski «kutayotgan» xabar avtomatik «tayyor bo'ldi» ga yangilanadi
```

### Admin panel

```text
⚙️ Admin panel → 👨‍🔧 Ustalar (faollashtirish/bloklash/o'chirish)
              → 📊 Statistika (jami/kutayotgan/tayyor/tushum + ustalar kesimida)
              → 📦 Buyurtmalar
              → ⚙️ Sozlamalar
```

---

## 5. GitHub'ga joylash

```bash
cd ustaxona_bot
git init
git add .
git commit -m "Ustaxona bot: buyurtmalarni boshqarish tizimi"
```

GitHub'da yangi **private** repository yarating, so'ng:

```bash
git remote add origin git@github.com:USERNAME/ustaxona_bot.git
git branch -M main
git push -u origin main
```

> ⚠️ `.env` fayli `.gitignore` da — **hech qachon** token va parollarni
> repository'ga qo'ymang. Faqat `.env.example` push qilinadi.

---

## 6. Tez-tez uchraydigan muammolar

| Muammo | Yechim |
|---|---|
| Guruhga e'lon bormayapti | `GROUP_ID` va topic ID'lar to'g'riligini tekshiring, botni qayta ishga tushiring |
| `/groupid` ishlamayapti | BotFather'da `/setprivacy` → Disable, botni guruhdan chiqarib qayta qo'shing |
| Yopiq topic'ga bot yozolmayapti | Bot admin emas — «Manage topics» huquqi bilan admin qiling |
| Migratsiya xatosi | `DATABASE_URL` to'g'riligini va Postgres ishlab turganini tekshiring |
| Usta menyu ko'rmayapti | Admin hali tasdiqlamagan — ⚙️ Admin panel → 👨‍🔧 Ustalar |
