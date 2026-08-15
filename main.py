import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

WELCOME = """أهلاً بك في بوت 5day للاستثمار الذكي.

يسعدنا انضمامك إلينا.

تعريف برنامج الاستثمار:
مدة الدورة: 5 أيام.
نظام الارباح: 500 دينار لكل 10,000 دينار وفق شروط الاستثمار.

الشروط والأحكام:
- يحق لكل مستخدم باقة واحدة فقط.
- يتم تجميد رأس المال لمدة 5 أيام.
- يمكن سحب الأرباح يوميا.
- يمكن التجديد بعد انتهاء الباقة.
- تتحرر الأرباح مع رأس المال بعد انتهاء المدة.

يرجى قراءة الشروط كاملة قبل الاشتراك."""

MAIN_MENU = [
    ["حسابي", "الباقات"],
    ["إيداع", "سحب"],
    ["الإحالة", "الدعم"],
    ["الوكلاء", "الشروط والأحكام"],
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        MAIN_MENU,
        resize_keyboard=True
    )

    await update.message.reply_text(
        WELCOME,
        reply_markup=keyboard
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    responses = {
        "حسابي": "قسم حسابي قيد الإعداد.",
        "الباقات": "قسم الباقات قيد الإعداد.",
        "إيداع": "قسم الإيداع قيد الإعداد.",
        "سحب": "قسم السحب قيد الإعداد.",
        "الإحالة": "قسم الإحالة قيد الإعداد.",
        "الدعم": "قسم الدعم قيد الإعداد.",
        "الوكلاء": "قسم الوكلاء قيد الإعداد.",
        "الشروط والأحكام": "قسم الشروط والأحكام قيد الإعداد.",
    }

    if text in responses:
        await update.message.reply_text(responses[text])


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        menu
    )
)

app.run_polling()
