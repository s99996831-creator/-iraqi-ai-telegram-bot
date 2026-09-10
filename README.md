# 🇮🇶 Iraqi AI Telegram Bot

بوت تيليگرام ذكاء اصطناعي يحچي باللهجة العراقية، بشخصية بنت مرحة، ويحتفظ بذاكرة طويلة الأمد لكل مستخدم.

## شنو بيه؟

- Telegram Bot API
- OpenAI Responses API
- SQLite database
- ذاكرة طويلة الأمد لكل Telegram user
- سجل آخر المحادثات
- `/memory` لعرض الذاكرة
- `/forget` لمسح الذاكرة
- `/clear` لمسح سجل المحادثة فقط
- Persona باللهجة العراقية
- لا يخزن كلمات المرور أو API keys ضمن الذاكرة
- كل مستخدم عنده ذاكرة منفصلة

## 1) المتطلبات

ثبت Python 3.11 أو أحدث.

تأكد من وجود:
- Telegram account
- Bot token من @BotFather
- OpenAI API key

Telegram يوضح أن إنشاء البوت يبدأ من @BotFather باستخدام `/newbot`، وأن التوكن لازم يبقى سرياً. راجع الدليل الرسمي:
https://core.telegram.org/bots/tutorial

## 2) إنشاء البوت

افتح Telegram وابحث عن:

@BotFather

ثم:

/newbot

اختار اسم للبوت، وبعدها username ينتهي بـ `bot`.

انسخ التوكن.

## 3) تجهيز المشروع

افتح Terminal داخل مجلد المشروع:

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4) إعداد الأسرار

انسخ:

```text
.env.example
```

إلى:

```text
.env
```

ثم افتحه وضع:

```env
TELEGRAM_BOT_TOKEN=توكن_البوت
OPENAI_API_KEY=مفتاح_OPENAI
OPENAI_MODEL=gpt-5.6-luna
DB_PATH=bot.db
```

لا ترسل `.env` لأي شخص ولا ترفعه إلى GitHub.

## 5) تشغيل البوت

```bash
python bot.py
```

إذا ظهر:

```text
Bot is running...
```

فالبوت اشتغل.

بعدها افتح البوت في Telegram واضغط Start.

## 6) الذاكرة

البوت عنده نوعين من الذاكرة:

### ذاكرة قصيرة
آخر 24 رسالة محفوظة لكل مستخدم حتى يفهم سياق السالفة.

### ذاكرة طويلة
أشياء مفيدة للمستقبل، مثل:
- الاسم أو اللقب المفضل
- أسلوب الكلام
- مشروع مستمر
- تفضيلات ثابتة

كل مستخدم عنده سجل منفصل حسب `telegram_id`.

## 7) الأوامر

```text
/start
/help
/memory
/forget
/clear
```

`/forget` يمسح الذاكرة الطويلة وسجل المحادثة.

`/clear` يمسح سجل المحادثة فقط ويخلي الذاكرة الطويلة.

## 8) ملاحظة مهمة عن التكلفة

هذا الإصدار يستخدم استدعاء OpenAI للرد واستدعاء إضافي لاستخراج الذاكرة.

يعني بعض الرسائل ممكن تكلف استدعاءين API.

إذا تريد تقلل التكلفة، نكدر لاحقاً نخلي استخراج الذاكرة:
- كل 5 رسائل
- أو فقط إذا المستخدم قال "تذكري"
- أو باستخدام structured output/tool واحد

## 9) التطوير بعد النسخة الأولى

النسخة التالية ممكن نضيف لها:

- لوحة تحكم Admin
- اشتراكات ومدفوعات
- صور وصوت
- Voice messages
- بحث بالذاكرة
- ذاكرة أقوى باستخدام PostgreSQL
- Redis للكاش
- Webhook بدل polling
- Docker + VPS
- جدولة رسائل للمستخدمين الذين بدأوا البوت
- شخصيات متعددة
- إعداد شخصية من داخل Telegram
- زر "امسحي هاي المعلومة"
- تصدير واستيراد الذاكرة
- حماية من spam وrate limits

## 10) التشغيل على VPS

على سيرفر Linux:

```bash
sudo apt update
sudo apt install python3 python3-venv -y

git clone YOUR_REPO
cd YOUR_REPO

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env

python bot.py
```

للتشغيل الدائم استخدم systemd أو Docker.

## البنية

```text
iraqi_ai_telegram_bot/
├── bot.py
├── ai.py
├── db.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## ملاحظة تقنية

البوت نفسه ما عنده "ذاكرة ChatGPT" تلقائياً. الذاكرة هنا معمولة كطبقة مستقلة فوق النموذج:

Telegram
   ↓
Python Bot
   ↓
SQLite Memory
   ↓
OpenAI Responses API
   ↓
الرد
