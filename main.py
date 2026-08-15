import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ============================================================
# الإعدادات الأساسية
# ============================================================

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8460661282


# ============================================================
# قاعدة البيانات
# ============================================================

# لاحقاً نربط قاعدة البيانات هنا.


# ============================================================
# رسالة الترحيب
# ============================================================

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


# ============================================================
# القائمة الرئيسية
# ============================================================

MAIN_MENU = [
    ["حسابي", "الباقات"],
    ["إيداع", "سحب"],
    ["الإحالة", "الدعم"],
    ["الشروط والأحكام"],
]


# ============================================================
# قائمة الإيداع
# ============================================================

DEPOSIT_MENU = [
    ["إيداع مباشر"],
    ["إيداع عن طريق وكيل"],
    ["رجوع للقائمة الرئيسية"],
]


# ============================================================
# قائمة الإيداع المباشر
# ============================================================

DIRECT_DEPOSIT_MENU = [
    ["رجوع للإيداع"],
    ["رجوع للقائمة الرئيسية"],
]

# ============================================================
# الباقات
# ============================================================
PACKAGES = {}

# من 10,000 إلى 100,000
for amount in range(10000, 100001, 10000):
    PACKAGES[amount] = {
        "amount": amount,
        "daily_profit": (amount // 10000) * 100,
        "total_profit": (amount // 10000) * 500,
    }

# من 100,000 إلى 1,000,000
for amount in range(100000, 1000001, 100000):
    PACKAGES[amount] = {
        "amount": amount,
        "daily_profit": (amount // 10000) * 100,
        "total_profit": (amount // 10000) * 500,
    }

# من 1,000,000 إلى 15,000,000
for amount in range(1000000, 15000001, 500000):
    PACKAGES[amount] = {
        "amount": amount,
        "daily_profit": (amount // 10000) * 100,
        "total_profit": (amount // 10000) * 500,
    }
# ============================================================
# قائمة الإدارة
# ============================================================

ADMIN_MENU = [
    ["المستخدمون", "إدارة الباقات"],
    ["الإيداعات", "السحوبات"],
    ["طرق الإيداع", "طرق السحب"],
    ["الوكلاء", "رسالة جماعية"],
    ["رجوع للقائمة الرئيسية"],
]


# ============================================================
# START
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = MAIN_MENU.copy()

    if update.effective_user.id == ADMIN_ID:
        keyboard.append(["لوحة الإدارة"])

    await update.message.reply_text(
        WELCOME,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# ============================================================
# حسابي
# ============================================================

async def account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# عرض الباقات
# ============================================================

async def packages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not PACKAGES:
        await update.message.reply_text(
            "لا توجد باقات متاحة حالياً."
        )
        return

    buttons = []

    for package in sorted(PACKAGES.values(), key=lambda x: x["amount"]):

        buttons.append([
            f'{package["amount"]:,} د.ع'
        ])

    buttons.append(["رجوع للقائمة الرئيسية"])

    await update.message.reply_text(
        "الباقات المتاحة:",
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True
        )
    )


# ============================================================
# تفاصيل الباقة
# ======================================================
async def package_details(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    amount_text = text.replace(" د.ع", "").replace(",", "").strip()

    try:
        amount = int(amount_text)
    except ValueError:
        await update.message.reply_text("الباقة غير موجودة.")
        return

    package = PACKAGES.get(amount)

    if not package:
        await update.message.reply_text("الباقة غير موجودة.")
        return

    buttons = [
        ["اشتراك"],
        ["رجوع"]
    ]

    await update.message.reply_text(
        f"""تفاصيل الباقة.

المبلغ: {amount:,} د.ع.
الربح اليومي: {package["daily_profit"]:,} د.ع.
إجمالي الربح خلال 5 أيام: {package["total_profit"]:,} د.ع.
مدة الدورة: 5 أيام.""",
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True
        )
    )

# ============================================================
# الإيداع
# ============================================================

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "اختر طريقة الإيداع:",
        reply_markup=ReplyKeyboardMarkup(
            DEPOSIT_MENU,
            resize_keyboard=True
        )
    )


# ============================================================
# الإيداع المباشر
# ============================================================

async def direct_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# الإيداع عن طريق وكيل
# ============================================================

async def agent_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# السحب
# ============================================================

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# الإحالة
# ============================================================

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# الدعم
# ============================================================

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# الشروط والأحكام
# ============================================================

async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# المستخدمون - ADMIN
# ============================================================

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# إدارة الباقات - ADMIN
# ============================================================

async def admin_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# إدارة الإيداعات - ADMIN
# ============================================================

async def admin_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# إدارة السحوبات - ADMIN
# ============================================================

async def admin_withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# طرق الإيداع - ADMIN
# ============================================================

async def admin_deposit_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# طرق السحب - ADMIN
# ============================================================

async def admin_withdraw_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# الوكلاء - ADMIN
# ============================================================

async def admin_agents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# الرسالة الجماعية - ADMIN
# ============================================================

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ============================================================
# لوحة الإدارة
# ============================================================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "لوحة الإدارة.",
        reply_markup=ReplyKeyboardMarkup(
            ADMIN_MENU,
            resize_keyboard=True
        )
    )


# ============================================================
# HANDLER الرئيسي للأزرار
# ============================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # ========================================================
    # لوحة الإدارة
    # ========================================================

    if text == "لوحة الإدارة":

        if update.effective_user.id == ADMIN_ID:
            await admin_panel(update, context)

        return

    # ========================================================
    # رجوع للقائمة الرئيسية
    # ========================================================

    if text == "رجوع للقائمة الرئيسية":

        keyboard = MAIN_MENU.copy()

        if update.effective_user.id == ADMIN_ID:
            keyboard.append(["لوحة الإدارة"])

        await update.message.reply_text(
            "تم الرجوع للقائمة الرئيسية.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

        return

    # ========================================================
    # الإيداع
    # ========================================================

    if text == "إيداع":
        await deposit(update, context)

    elif text == "إيداع مباشر":
        await direct_deposit(update, context)

    elif text == "إيداع عن طريق وكيل":
        await agent_deposit(update, context)

    elif text == "رجوع للإيداع":

        await deposit(update, context)

    # ========================================================
    # أقسام المستخدم
    # ========================================================

    elif text == "حسابي":
        await account(update, context)

    elif text == "الباقات":
        await packages(update, context)

    elif text.endswith(" د.ع"):
        await package_details(update, context)

    elif text == "سحب":
        await withdraw(update, context)

    elif text == "الإحالة":
        await referral(update, context)

    elif text == "الدعم":
        await support(update, context)

    elif text == "الشروط والأحكام":
        await terms(update, context)

    # ========================================================
    # أقسام الإدارة
    # ========================================================

    elif text == "المستخدمون":
        await admin_users(update, context)

    elif text == "إدارة الباقات":
        await admin_packages(update, context)

    elif text == "الإيداعات":
        await admin_deposits(update, context)

    elif text == "السحوبات":
        await admin_withdrawals(update, context)

    elif text == "طرق الإيداع":
        await admin_deposit_methods(update, context)

    elif text == "طرق السحب":
        await admin_withdraw_methods(update, context)

    elif text == "الوكلاء":
        await admin_agents(update, context)

    elif text == "رسالة جماعية":
        await admin_broadcast(update, context)


# ============================================================
# تشغيل البوت
# ============================================================

app = Application.builder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        button_handler
    )
)

app.run_polling()
