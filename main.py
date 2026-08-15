# ===== الاستيرادات =====

import os
import time

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


# ===== الإعدادات الأساسية =====

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 8460661282
BOT_USERNAME = "FAIVEDAY5_bot"


# ===== إعدادات الأرباح =====

PACKAGE_DAYS = 5
PROFIT_PER_10000 = 100


# ===== إعدادات الإحالة =====

REFERRAL_RATE = 0.05


# ===== إعدادات السحب =====

MIN_WITHDRAW = 8000
WITHDRAW_FEE = 1000


# ===== تعريف الحالات =====

STATE_NONE = "none"

STATE_DEPOSIT = "deposit"
STATE_DEPOSIT_AMOUNT = "deposit_amount"
STATE_DEPOSIT_PHOTO = "deposit_photo"

STATE_WITHDRAW = "withdraw"
STATE_WITHDRAW_AMOUNT = "withdraw_amount"
STATE_WITHDRAW_DETAILS = "withdraw_details"

STATE_SUPPORT = "support"
STATE_ADMIN_REPLY = "admin_reply"


# ===== تعريف الأزرار الشفافة =====

DEPOSIT_CONFIRM = "deposit_confirm"
DEPOSIT_CANCEL = "deposit_cancel"
DEPOSIT_APPROVE = "deposit_approve"
DEPOSIT_REJECT = "deposit_reject"

WITHDRAW_CONFIRM = "withdraw_confirm"
WITHDRAW_CANCEL = "withdraw_cancel"
WITHDRAW_APPROVE = "withdraw_approve"
WITHDRAW_REJECT = "withdraw_reject"

SUPPORT_REPLY = "support_reply"
SUPPORT_CANCEL = "support_cancel"


# ===== بيانات المستخدمين =====

users = {}

deposit_requests = {}
withdraw_requests = {}
support_requests = {}


# ===== بيانات الإحالة =====

# صاحب الرابط الذي جاء منه المستخدم.
# مثال:
# user["referrer_id"] = 123456789

# عند تفعيل الصديق لباقة:
# referral_profit = package_amount * REFERRAL_RATE
#
# مثال:
# 100,000 × 5% = 5,000 د.ع.


# ===== رسالة الترحيب =====

WELCOME_MESSAGE = """
أهلاً وسهلاً بك في بوت 5DAY.

اختار القسم المطلوب من القائمة أدناه.
"""


# ===== كيبورد المستخدم =====

def user_keyboard(user_id):

    keyboard = [
        ["الباقات", "حسابي"],
        ["إيداع", "سحب"],
        ["الإحالة", "حالة الباقة"],
        ["الدعم"]
    ]

    if user_id == ADMIN_ID:
        keyboard.append(["لوحة الإدارة"])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ===== كيبورد الإدارة =====

def admin_keyboard():

    keyboard = [
        ["طلبات الإيداع", "طلبات السحب"],
        ["رسائل الدعم", "المستخدمين"],
        ["الإحصائيات"],
        ["رجوع"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ===== أمر البدء =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=user_keyboard(user_id)
    )


# ===== حسابي =====

async def account(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pass


# ===== الباقات =====

async def packages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pass


# ===== حالة الباقة =====

async def package_status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pass


# ===== الإيداع =====

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pass


# ===== استقبال صورة الإيداع =====

async def deposit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pass


# ===== السحب =====

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pass


# ===== الإحالة =====

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

    await update.message.reply_text(
        f"""
رابط الإحالة الخاص بك:

{link}

نسبة الإحالة:
5%

تحصل على 5% من قيمة باقة صديقك عند تفعيلها.
"""
    )


# ===== تفعيل ربح الإحالة =====

async def give_referral_profit(
    user_id,
    package_amount,
    context
):

    user = users.get(user_id)

    if not user:
        return

    referrer_id = user.get("referrer_id")

    if not referrer_id:
        return

    referral_profit = int(
        package_amount * REFERRAL_RATE
    )

    referrer = users.get(referrer_id)

    if not referrer:
        return

    referrer["referral_profit"] = (
        referrer.get("referral_profit", 0)
        + referral_profit
    )

    # هذا الرصيد لاحقاً نربطه بالنظام المالي بعد إكماله.
    referrer["balance"] = (
        referrer.get("balance", 0)
        + referral_profit
    )

    await context.bot.send_message(
        chat_id=referrer_id,
        text=f"""
حصلت على ربح إحالة.

باقة صديقك:
{package_amount:,} د.ع.

ربح الإحالة:
{referral_profit:,} د.ع.

النسبة:
5%
"""
    )


# ===== الدعم =====

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pass


# ===== لوحة الإدارة =====

async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "لوحة الإدارة.",
        reply_markup=admin_keyboard()
    )


# ===== أزرار الإدارة =====

async def admin_buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text

    if text == "طلبات الإيداع":
        pass

    elif text == "طلبات السحب":
        pass

    elif text == "رسائل الدعم":
        pass

    elif text == "المستخدمين":
        pass

    elif text == "الإحصائيات":
        pass

    elif text == "رجوع":
        await start(update, context)


# ===== الأزرار الشفافة =====

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    if data.startswith(DEPOSIT_APPROVE):
        pass

    elif data.startswith(DEPOSIT_REJECT):
        pass

    elif data.startswith(WITHDRAW_APPROVE):
        pass

    elif data.startswith(WITHDRAW_REJECT):
        pass

    elif data.startswith(SUPPORT_REPLY):
        pass


# ===== معالج الرسائل =====

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    if text == "لوحة الإدارة":

        await admin_panel(update, context)

    elif text == "حسابي":

        await account(update, context)

    elif text == "الباقات":

        await packages(update, context)

    elif text == "إيداع":

        await deposit(update, context)

    elif text == "سحب":

        await withdraw(update, context)

    elif text == "الإحالة":

        await referral(update, context)

    elif text == "حالة الباقة":

        await package_status(update, context)

    elif text == "الدعم":

        await support(update, context)


# ===== معالج الصور =====

async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    pass


# ===== تشغيل البوت =====

app = Application.builder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CallbackQueryHandler(callback_handler)
)

app.add_handler(
    MessageHandler(
        filters.PHOTO,
        photo_handler
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler
    )
)


# ===== نهاية الكود =====

app.run_polling()
