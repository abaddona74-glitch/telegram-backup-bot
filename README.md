# 🕵️ Telegram Backup Bot

**IceGlassBot** kabi ishlaydigan shaxsiy Telegram bot:

| Funksiya | Tavsif |
|----------|--------|
| 🗑 O'chirilgan xabarlar | Kontakt xabarni o'chirishda darhol xabar beradi |
| ✏️ Tahrirlangan xabarlar | Eski va yangi matnni solishtirib ko'rsatadi |
| 👁 One-time media | View-once foto/video avtomatik saqlanadi |

---

## 🚀 Boshlash

### 1. BotFather'dan token oling

[@BotFather](https://t.me/BotFather) ga boring → `/newbot` → token oling

### 2. O'z Telegram ID'ingizni bilib oling

[@userinfobot](https://t.me/userinfobot) ga `/start` yuboring

### 3. `.env` faylini yarating

```bash
cp .env.example .env
```

`.env` ichiga to'ldiring:
```
BOT_TOKEN=1234567890:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OWNER_ID=123456789
```

### 4. Lokal ishga tushirish (test uchun)

```bash
pip install -r requirements.txt
python -m bot.main
```

---

## ☁️ Railway'da Deploy qilish

### 1. GitHub'ga push qiling

```bash
git init
git add .
git commit -m "Initial bot"
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/telegram-backup-bot.git
git push -u origin main
```

### 2. Railway'da loyiha yarating

1. [railway.app](https://railway.app) ga kiring (GitHub bilan)
2. **New Project** → **Deploy from GitHub repo**
3. Repo'ni tanlang

### 3. Environment Variables qo'shing

Railway dashboard → Variables:

| Kalit | Qiymat |
|-------|--------|
| `BOT_TOKEN` | BotFather'dan olingan token |
| `OWNER_ID` | Sizning Telegram ID |
| `WEBHOOK_HOST` | Railway domeningiz (masalan `https://xxx.railway.app`) |
| `WEBHOOK_PORT` | `8080` |

### 4. Botni Telegram'ga ulang

1. **Settings** → **Telegram Business** → **Chat Automation**
2. Botingizni (`@your_bot`) tanlang
3. "All chats" yoki kerakli chatlarni belgilang
4. **Save** ✅

---

## 📁 Loyiha strukturasi

```
telegram_backup/
├── bot/
│   ├── main.py              # Asosiy ishga tushirish
│   ├── config.py            # .env sozlamalar
│   ├── database.py          # SQLite operatsiyalar
│   ├── handlers/
│   │   ├── business.py      # Kelgan xabarlar → DB saqlash
│   │   ├── deleted.py       # O'chirilgan xabarlar
│   │   ├── edited.py        # Tahrirlangan xabarlar
│   │   └── start.py         # /start buyruq
│   └── utils/
│       ├── formatters.py    # Xabar formatlash
│       └── media_saver.py   # Media ma'lumotlarini ajratish
├── .env.example
├── requirements.txt
├── Dockerfile
└── railway.toml
```

---

## ⚠️ Muhim eslatmalar

- **Telegram Business yoki Telegram Premium** kerak (Chat Automation uchun)
- Bot faqat **o'zingizning** chatlaringizni kuzatadi (personal)
- View-once media faqat siz ulagan chatlardan ishlaydi
- Ma'lumotlar SQLite'da lokal saqlanadi (Railway'da restart bo'lsa tozalanishi mumkin — persistent storage qo'shing)

---

## 🔧 Sozlamalar

`.env` fayli orqali boshqariladi. Barcha parametrlar `.env.example` da ko'rsatilgan.
