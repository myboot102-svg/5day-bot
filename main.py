# ===== الاستيرادات =====

import os

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

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8460661282
BOT_USERNAME = "FAIVEDAY5_bot"

if not TOKEN:
    raise RuntimeError("BOT_TOKEN غير موجود في Railway Variables")


# ===== إعدادات الأرباح والإحالة =====

PACKAGE_DAYS = 5
DAILY_PROFIT_PER_10000 = 100
TOTAL_PROFIT_PER_10000 = 500
REFERRAL_RATE = 0.05


# ===== تعريف الحالات =====

STATE_NONE = "none"
STATE_ADD_PACKAGE = "add_package"
STATE_EDIT_PACKAGE = "edit_package"
STATE_ADD_DEPOSIT_WALLET = "add_deposit_wallet"
STATE_ADD_WITHDRAW_WALLET = "add_withdraw_wallet"
STATE_ADD_AGENT = "add_agent"
STATE_BROADCAST = "broadcast"
STATE_SUPPORT = "support"
STATE_ADMIN_REPLY = "admin_reply"


# ===== تعريف الأزرار الشفافة =====

CB_PACKAGE_ADD = "package_add"
CB_PACKAGE_EDIT = "package_edit"
CB_PACKAGE_DELETE = "package_delete"

CB_DEPOSIT_WALLET_DELETE = "deposit_wallet_delete"
CB_WITHDRAW_WALLET_DELETE = "withdraw_wallet_delete"

CB_AGENT_DELETE = "agent_delete"

CB_SUPPORT_REPLY = "support_reply"


# ===== البيانات =====

users = {}

packages_data = {
    "10000": {"amount": 10000, "daily_profit": 100, "total_profit": 500, "days": 5, "active": True},
    "20000": {"amount": 20000, "daily_profit": 200, "total_profit": 1000, "days": 5, "active": True},
    "30000": {"amount": 30000, "daily_profit": 300, "total_profit": 1500, "days": 5, "active": True},
    "40000": {"amount": 40000, "daily_profit": 400, "total_profit": 2000, "days": 5, "active": True},
    "50000": {"amount": 50000, "daily_profit": 500, "total_profit": 2500, "days": 5, "active": True},
    "60000": {"amount": 60000, "daily_profit": 600, "total_profit": 3000, "days": 5, "active": True},
    "70000": {"amount": 70000, "daily_profit": 700, "total_profit": 3500, "days": 5, "active": True},
    "80000": {"amount": 80000, "daily_profit": 800, "total_profit": 4000, "days": 5, "active": True},
    "90000": {"amount": 90000, "daily_profit": 900, "total_profit": 4500, "days": 5, "active": True},
    "100000": {"amount": 100000, "daily_profit": 1000, "total_profit": 5000, "days": 5, "active": True},

    "200000": {"amount": 200000, "daily_profit": 2000, "total_profit": 10000, "days": 5, "active": True},
    "300000": {"amount": 300000, "daily_profit": 3000, "total_profit": 15000, "days": 5, "active": True},
    "400000": {"amount": 400000, "daily_profit": 4000, "total_profit": 20000, "days": 5, "active": True},
    "500000": {"amount": 500000, "daily_profit": 5000, "total_profit": 25000, "days": 5, "active": True},
    "600000": {"amount": 600000, "daily_profit": 6000, "total_profit": 30000, "days": 5, "active": True},
    "700000": {"amount": 700000, "daily_profit": 7000, "total_profit": 35000, "days": 5, "active": True},
    "800000": {"amount": 800000, "daily_profit": 8000, "total_profit": 40000, "days": 5, "active": True},
    "900000": {"amount": 900000, "daily_profit": 9000, "total_profit": 45000, "days": 5, "active": True},

    "1000000": {"amount": 1000000, "daily_profit": 10000, "total_profit": 50000, "days": 5, "active": True},
    "1500000": {"amount": 1500000, "daily_profit": 15000, "total_profit": 75000, "days": 5, "active": True},
    "2000000": {"amount": 2000000, "daily_profit": 20000, "total_profit": 100000, "days": 5, "active": True},
    "2500000": {"amount": 2500000, "daily_profit": 25000, "total_profit": 125000, "days": 5, "active": True},
    "3000000": {"amount": 3000000, "daily_profit": 30000, "total_profit": 150000, "days": 5, "active": True},
    "3500000": {"amount": 3500000, "daily_profit": 35000, "total_profit": 175000, "days": 5, "active": True},
    "4000000": {"amount": 4000000, "daily_profit": 40000, "total_profit": 200000, "days": 5, "active": True},
    "4500000": {"amount": 4500000, "daily_profit": 45000, "total_profit": 225000, "days": 5, "active": True},
    "5000000": {"amount": 5000000, "daily_profit": 50000, "total_profit": 250000, "days": 5, "active": True},
    "5500000": {"amount": 5500000, "daily_profit": 55000, "total_profit": 275000, "days": 5, "active": True},
    "6000000": {"amount": 6000000, "daily_profit": 60000, "total_profit": 300000, "days": 5, "active": True},
    "6500000": {"amount": 6500000, "daily_profit": 65000, "total_profit": 325000, "days": 5, "active": True},
    "7000000": {"amount": 7000000, "daily_profit": 70000, "total_profit": 350000, "days": 5, "active": True},
    "7500000": {"amount": 7500000, "daily_profit": 75000, "total_profit": 375000, "days": 5, "active": True},
    "8000000": {"amount": 8000000, "daily_profit": 80000, "total_profit": 400000, "days": 5, "active": True},
    "8500000": {"amount": 8500000, "daily_profit": 85000, "total_profit": 425000, "days": 5, "active": True},
    "9000000": {"amount": 9000000, "daily_profit": 90000, "total_profit": 450000, "days": 5, "active": True},
    "9500000": {"amount": 9500000, "daily_profit": 95000, "total_profit": 475000, "days": 5, "active": True},
    "10000000": {"amount": 10000000, "daily_profit": 100000, "total_profit": 500000, "days": 5, "active": True},
    "10500000": {"amount": 10500000, "daily_profit": 105000, "total_profit": 525000, "days": 5, "active": True},
    "11000000": {"amount": 11000000, "daily_profit": 110000, "total_profit": 550000, "days": 5, "active": True},
    "11500000": {"amount": 11500000, "daily_profit": 115000, "total_profit": 575000, "days": 5, "active": True},
    "12000000": {"amount": 12000000, "daily_profit": 120000, "total_profit": 600000, "days": 5, "active": True},
    "12500000": {"amount": 12500000, "daily_profit": 125000, "total_profit": 625000, "days": 5, "active": True},
    "13000000": {"amount": 13000000, "daily_profit": 130000, "total_profit": 650000, "days": 5, "active": True},
    "13500000": {"amount": 13500000, "daily_profit": 135000, "total_profit": 675000, "days": 5, "active": True},
    "14000000": {"amount": 14000000, "daily_profit": 140000, "total_profit": 700000, "days": 5, "active": True},
    "14500000": {"amount": 14500000, "daily_profit": 145000, "total_profit": 725000, "days": 5, "active": True},
    "15000000": {"amount": 15000000, "daily_profit": 150000, "total_profit": 750000, "days": 5, "active": True}
}

deposit_wallets = {}

withdraw_wallets = {}

agents = {}

support_messages = {}


# ===== الحالات =====

user_states = {}


# ===== الحصول على مستخدم =====

def get_user(user_id):

    if user_id not in users:

        users[user_id] = {
            "name": "",
            "username": "",
            "referrer_id": None,
            "referrals": 0,
            "referral_profit": 0
        }

    return users[user_id]


# ===== تغيير حالة المستخدم =====

def set_state(user_id, state):

    user_states[user_id] = state


def get_state(user_id):

    return user_states.get(
        user_id,
        STATE_NONE
    )


def clear_state(user_id):

    user_states[user_id] = STATE_NONE


# ===== رسالة الترحيب =====

WELCOME_MESSAGE = """
━━━━━━━━━━━━━━━━━━

أهلاً وسهلاً بك في بوت 5DAY.

اختار القسم المطلوب من القائمة.

━━━━━━━━━━━━━━━━━━
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
        keyboard.append(
            ["لوحة الإدارة"]
        )

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ===== كيبورد الإدارة =====

def admin_keyboard():

    keyboard = [
        ["إدارة الباقات"],
        ["محافظ الإيداع", "محافظ السحب"],
        ["إدارة الوكلاء"],
        ["طلبات الإيداع", "طلبات السحب"],
        ["رسائل الدعم"],
        ["المستخدمين"],
        ["رسالة جماعية"],
        ["الإحصائيات"],
        ["رجوع"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ===== أمر البدء =====

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    user = get_user(user_id)

    user["name"] = update.effective_user.full_name or ""
    user["username"] = update.effective_user.username or ""

    clear_state(user_id)

    # ===== الإحالة =====

    if context.args:

        argument = context.args[0]

        if argument.startswith("ref_"):

            try:

                referrer_id = int(
                    argument.replace(
                        "ref_",
                        "",
                        1
                    )
                )

                if (
                    referrer_id != user_id
                    and user["referrer_id"] is None
                ):

                    user["referrer_id"] = referrer_id

                    referrer = get_user(
                        referrer_id
                    )

                    referrer["referrals"] += 1

                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text="انضم صديق جديد عن طريق رابط الإحالة الخاص بك."
                    )

            except:
                pass

    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=user_keyboard(user_id)
    )


# ===== حسابي =====

async def account(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = get_user(
        update.effective_user.id
    )

    await update.message.reply_text(
        f"""
━━━━━━━━━━━━━━━━━━
حسابي
━━━━━━━━━━━━━━━━━━

الاسم: {user["name"]}
اليوزر: @{user["username"] or "بدون يوزر"}

عدد الإحالات:
{user["referrals"]}

أرباح الإحالة:
{user["referral_profit"]:,} د.ع.

━━━━━━━━━━━━━━━━━━
"""
    )


# ===== قسم الباقات =====

async def package_message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text.strip()

    if text == "رجوع للقائمة الرئيسية":
        await start(update, context)
        return

    if not text.endswith("د.ع"):
        return

    try:
        amount = int(
            text.replace("د.ع", "")
                .replace(",", "")
                .strip()
        )
    except ValueError:
        return

    package = packages_data.get(str(amount))

    if not package or not package.get("active", True):
        await update.message.reply_text(
            "هذه الباقة غير متاحة حالياً."
        )
        return

    daily = package.get("daily_profit", 0)
    total = package.get("total_profit", 0)
    days = package.get("days", 5)

    keyboard = [
        ["اشتراك"],
        ["العودة للباقات"]
    ]

    await update.message.reply_text(
        f"تفاصيل الباقة.\n\n"
        f"المبلغ: {amount:,} د.ع\n"
        f"المدة: {days} أيام\n"
        f"العائد اليومي المعلن: {daily:,} د.ع\n"
        f"إجمالي العائد المعلن: {total:,} د.ع\n\n"
        f"إذا تريد المتابعة اضغط اشتراك.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )
# ===== تأكيد الاشتراك =====

async def package_confirm(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not context.user_data.get("package_confirm"):
        return

    text = update.message.text.strip()

    if text == "رجوع":

        context.user_data["package_confirm"] = False
        context.user_data["selected_package"] = None

        await packages(update, context)
        return

    if text != "اشتراك":
        return

    package_id = context.user_data.get(
        "selected_package"
    )

    package = packages_data.get(package_id)

    if not package:
        await update.message.reply_text(
            "الباقة غير موجودة حالياً."
        )
        return

    user_id = update.effective_user.id
    user = get_user(user_id)

    amount = int(package["amount"])

    # التأكد من الرصيد
    if int(user.get("balance", 0)) < amount:

        await update.message.reply_text(
            f"""رصيدك غير كافي.

سعر الباقة:
{amount:,} د.ع.

رصيدك الحالي:
{int(user.get("balance", 0)):,} د.ع."""
        )

        return

    # منع الاشتراك بباقة ثانية إذا عنده باقة فعالة
    if user.get("package") and user["package"].get("active"):

        await update.message.reply_text(
            "لديك باقة فعالة حالياً."
        )

        return

    # خصم قيمة الباقة
    user["balance"] -= amount

    # تفعيل الباقة
    user["package"] = {
        "id": package_id,
        "amount": amount,
        "daily_profit": int(package["daily_profit"]),
        "total_profit": int(package["total_profit"]),
        "days": int(package["days"]),
        "days_paid": 0,
        "start_time": int(time.time()),
        "active": True
    }

    # تحديث الإحصائيات
    user["total_packages"] = (
        int(user.get("total_packages", 0)) + 1
    )

    user["total_deposited"] = (
        int(user.get("total_deposited", 0))
        + amount
    )

    context.user_data["package_confirm"] = False
    context.user_data["selected_package"] = None

    # رجوع للكيبورد الرئيسي
    keyboard = [
        [
            KeyboardButton("الباقات"),
            KeyboardButton("الإيداع")
        ],
        [
            KeyboardButton("السحب"),
            KeyboardButton("حسابي")
        ],
        [
            KeyboardButton("الإحالة"),
            KeyboardButton("الدعم")
        ]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        f"""تم تفعيل الباقة بنجاح.

المبلغ:
{amount:,} د.ع.

الربح اليومي:
{int(package["daily_profit"]):,} د.ع.

إجمالي الربح:
{int(package["total_profit"]):,} د.ع.

مدة الباقة:
{int(package["days"])} أيام.

تم خصم مبلغ الباقة من رصيدك.""",
        reply_markup=reply_markup
    )

# ===== حالة الباقة =====

async def package_status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "حالة الباقة سيتم عرضها هنا."
    )


# ===== الإيداع =====

async def deposit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not deposit_wallets:

        await update.message.reply_text(
            "لا توجد محافظ إيداع متاحة حالياً."
        )

        return

    buttons = []

    for wallet_id, wallet in deposit_wallets.items():

        buttons.append([
            InlineKeyboardButton(
                wallet["name"],
                callback_data=f"deposit_wallet:{wallet_id}"
            )
        ])

    await update.message.reply_text(
        "اختار طريقة الإيداع:",
        reply_markup=InlineKeyboardMarkup(
            buttons
        )
    )


# ===== السحب =====

async def withdraw(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not withdraw_wallets:

        await update.message.reply_text(
            "لا توجد طرق سحب متاحة حالياً."
        )

        return

    buttons = []

    for wallet_id, wallet in withdraw_wallets.items():

        buttons.append([
            InlineKeyboardButton(
                wallet["name"],
                callback_data=f"withdraw_wallet:{wallet_id}"
            )
        ])

    await update.message.reply_text(
        "اختار طريقة السحب:",
        reply_markup=InlineKeyboardMarkup(
            buttons
        )
    )


# ===== الإحالة =====

async def referral(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    user = get_user(user_id)

    link = (
        f"https://t.me/"
        f"{BOT_USERNAME}"
        f"?start=ref_{user_id}"
    )

    await update.message.reply_text(
        f"""
━━━━━━━━━━━━━━━━━━
الإحالة
━━━━━━━━━━━━━━━━━━

رابط الإحالة:

{link}

نسبة الإحالة:
5%

عدد الإحالات:
{user["referrals"]}

أرباح الإحالة:
{user["referral_profit"]:,} د.ع.

━━━━━━━━━━━━━━━━━━
"""
    )


# ===== الدعم =====

async def support(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    set_state(
        update.effective_user.id,
        STATE_SUPPORT
    )

    await update.message.reply_text(
        "اكتب رسالتك للدعم."
    )


# ===== لوحة الإدارة =====

async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    clear_state(
        update.effective_user.id
    )

    await update.message.reply_text(
        "لوحة الإدارة:",
        reply_markup=admin_keyboard()
    )


# ===== إدارة الباقات =====

async def admin_packages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "إضافة باقة",
                callback_data=CB_PACKAGE_ADD
            )
        ]
    ]

    for package_id, package in packages_data.items():

        keyboard.append([
            InlineKeyboardButton(
                f'تعديل {package["amount"]:,}',
                callback_data=f"{CB_PACKAGE_EDIT}:{package_id}"
            ),
            InlineKeyboardButton(
                "حذف",
                callback_data=f"{CB_PACKAGE_DELETE}:{package_id}"
            )
        ])

    await update.message.reply_text(
        "إدارة الباقات:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# ===== إضافة باقة =====

async def add_package_start(
    query,
    context
):

    set_state(
        query.from_user.id,
        STATE_ADD_PACKAGE
    )

    await query.message.reply_text(
        """
اكتب بيانات الباقة بهذا الشكل:

المبلغ,الربح_اليومي,الربح_الكلي,المدة

مثال:

100000,1000,5000,5
"""
    )


# ===== محافظ الإيداع =====

async def admin_deposit_wallets(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "إضافة محفظة",
                callback_data="deposit_wallet_add"
            )
        ]
    ]

    for wallet_id, wallet in deposit_wallets.items():

        keyboard.append([
            InlineKeyboardButton(
                f'{wallet["name"]}',
                callback_data=f"deposit_wallet_delete:{wallet_id}"
            )
        ])

    await update.message.reply_text(
        "محافظ الإيداع:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# ===== محافظ السحب =====

async def admin_withdraw_wallets(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "إضافة محفظة",
                callback_data="withdraw_wallet_add"
            )
        ]
    ]

    for wallet_id, wallet in withdraw_wallets.items():

        keyboard.append([
            InlineKeyboardButton(
                f'{wallet["name"]}',
                callback_data=f"withdraw_wallet_delete:{wallet_id}"
            )
        ])

    await update.message.reply_text(
        "محافظ السحب:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# ===== إدارة الوكلاء =====

async def admin_agents(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "إضافة وكيل",
                callback_data="agent_add"
            )
        ]
    ]

    for agent_id, agent in agents.items():

        keyboard.append([
            InlineKeyboardButton(
                agent["name"],
                callback_data=f"agent_delete:{agent_id}"
            )
        ])

    await update.message.reply_text(
        "إدارة الوكلاء:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# ===== الرسالة الجماعية =====

async def broadcast_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    set_state(
        update.effective_user.id,
        STATE_BROADCAST
    )

    await update.message.reply_text(
        "اكتب الرسالة التي تريد إرسالها للمستخدمين."
    )


# ===== المستخدمين =====

async def admin_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        f"عدد المستخدمين المسجلين: {len(users)}"
    )


# ===== الإحصائيات =====

async def admin_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        f"""
الإحصائيات:

عدد المستخدمين:
{len(users)}

عدد الباقات:
{len(packages_data)}

محافظ الإيداع:
{len(deposit_wallets)}

محافظ السحب:
{len(withdraw_wallets)}

الوكلاء:
{len(agents)}
"""
    )


# ===== أزرار الإدارة =====

async def admin_buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text

    if text == "إدارة الباقات":
        await admin_packages(update, context)

    elif text == "محافظ الإيداع":
        await admin_deposit_wallets(update, context)

    elif text == "محافظ السحب":
        await admin_withdraw_wallets(update, context)

    elif text == "إدارة الوكلاء":
        await admin_agents(update, context)

    elif text == "طلبات الإيداع":
        await update.message.reply_text(
            "طلبات الإيداع."
        )

    elif text == "طلبات السحب":
        await update.message.reply_text(
            "طلبات السحب."
        )

    elif text == "رسائل الدعم":
        await update.message.reply_text(
            "رسائل الدعم."
        )

    elif text == "المستخدمين":
        await admin_users(update, context)

    elif text == "رسالة جماعية":
        await broadcast_start(update, context)

    elif text == "الإحصائيات":
        await admin_stats(update, context)

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

    if data == CB_PACKAGE_ADD:

        await add_package_start(
            query,
            context
        )

        return

    if data.startswith(
        f"{CB_PACKAGE_DELETE}:"
    ):

        package_id = data.split(
            ":",
            1
        )[1]

        packages_data.pop(
            package_id,
            None
        )

        await query.message.reply_text(
            "تم حذف الباقة."
        )

        return

    if data.startswith("package_view:"):

        package_id = data.split(
            ":",
            1
        )[1]

        await package_view(
            query,
            package_id
        )

        return

    if data.startswith(
        "deposit_wallet_delete:"
    ):

        wallet_id = data.split(
            ":",
            1
        )[1]

        deposit_wallets.pop(
            wallet_id,
            None
        )

        await query.message.reply_text(
            "تم حذف محفظة الإيداع."
        )

        return

    if data.startswith(
        "withdraw_wallet_delete:"
    ):

        wallet_id = data.split(
            ":",
            1
        )[1]

        withdraw_wallets.pop(
            wallet_id,
            None
        )

        await query.message.reply_text(
            "تم حذف محفظة السحب."
        )

        return

    if data.startswith(
        "agent_delete:"
    ):

        agent_id = data.split(
            ":",
            1
        )[1]

        agents.pop(
            agent_id,
            None
        )

        await query.message.reply_text(
            "تم حذف الوكيل."
        )

        return


# ===== استقبال البيانات =====

async def message_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id
    text = update.message.text

    state = get_state(user_id)

    # ===== حالات الإدارة =====

    if (
        user_id == ADMIN_ID
        and state == STATE_ADD_PACKAGE
    ):

        parts = [
            x.strip()
            for x in text.split(",")
        ]

        if len(parts) != 4:
            await update.message.reply_text(
                "الصيغة غير صحيحة."
            )
            return

        try:

            amount = int(parts[0])
            daily = int(parts[1])
            total = int(parts[2])
            days = int(parts[3])

            package_id = str(amount)

            packages_data[package_id] = {
                "amount": amount,
                "daily_profit": daily,
                "total_profit": total,
                "days": days,
                "active": True
            }

            clear_state(user_id)

            await update.message.reply_text(
                "تمت إضافة الباقة."
            )

        except ValueError:

            await update.message.reply_text(
                "تأكد من كتابة الأرقام بشكل صحيح."
            )

        return

    if (
        user_id == ADMIN_ID
        and state == STATE_BROADCAST
    ):

        sent = 0
        failed = 0

        for target_id in users:

            try:

                await context.bot.send_message(
                    chat_id=target_id,
                    text=text
                )

                sent += 1

            except:

                failed += 1

        clear_state(user_id)

        await update.message.reply_text(
            f"""
تم إرسال الرسالة الجماعية.

تم الإرسال:
{sent}

فشل الإرسال:
{failed}
"""
        )

        return

    # ===== أزرار الإدارة =====

    if user_id == ADMIN_ID:

        admin_texts = [
            "إدارة الباقات",
            "محافظ الإيداع",
            "محافظ السحب",
            "إدارة الوكلاء",
            "طلبات الإيداع",
            "طلبات السحب",
            "رسائل الدعم",
            "المستخدمين",
            "رسالة جماعية",
            "الإحصائيات",
            "رجوع"
        ]

        if text in admin_texts:

            await admin_buttons(
                update,
                context
            )

            return

    # ===== أزرار المستخدم =====

    if text == "لوحة الإدارة":

        await admin_panel(
            update,
            context
        )

    elif text == "الباقات":

        await packages(
            update,
            context
        )

    elif text == "حسابي":

        await account(
            update,
            context
        )

    elif text == "إيداع":

        await deposit(
            update,
            context
        )

    elif text == "سحب":

        await withdraw(
            update,
            context
        )

    elif text == "الإحالة":

        await referral(
            update,
            context
        )

    elif text == "حالة الباقة":

        await package_status(
            update,
            context
        )

    elif text == "الدعم":

        await support(
            update,
            context
        )


# ===== تشغيل البوت =====

app = Application.builder().token(TOKEN).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

# ===== هاندل أزرار الباقات =====

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_router
    )
)

app.add_handler(
    CallbackQueryHandler(
        callback_handler
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_router
    )
)

app.run_polling()
