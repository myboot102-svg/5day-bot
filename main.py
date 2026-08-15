import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

WELCOME = """أهلاً بك في بوت 5day للاستثمار الذكي.

يسعدنا انضمامك إلينا.

تعريف برنامج الاستثمار:
مدة الدورة: 5 أيام.
نظام البرنامج: 500 دينار لكل 10,000 دينار وفق شروط البرنامج.

الشروط والأحكام:
- يحق لكل مستخدم باقة واحدة فقط.
- يتم تجميد رأس المال لمدة 5 أيام.
- يمكن سحب الأرباح وفق آلية البرنامج.
- يمكن التجديد بعد انتهاء الباقة.
- تتحرر الأرباح مع رأس المال بعد انتهاء المدة.

يرجى قراءة الشروط كاملة قبل الاشتراك.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME)

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
