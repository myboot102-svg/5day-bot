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

from datetime import datetime
from datetime import datetime, timedelta

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

packages_data = {}

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
            "join_date": datetime.now(),

            "balance": 0,

            "packages_count": 0,
            "total_capital": 0,
            "total_profit": 0,

            "active_package": None,

            "referrer_id": None,
            "referrals": 0,
            "referral_profit": 0,

            "deposit_count": 0,
            "profit_withdrawals": 0,
            "blocked": False
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
    user_id = update.effective_user.id
    user = get_user(user_id)

    # الرصيد الحالي
    balance = user.get("balance", 0)

    # عدد الباقات المشترك بها عبر الوقت
    packages_count = user.get("packages_count", 0)

    # إجمالي الإيداعات / رأس المال
    total_capital = user.get("total_capital", 0)

    # إجمالي الأرباح من الباقات
    total_profit = user.get("total_profit", 0)

    # إجمالي رأس المال + الأرباح
    total_all = total_capital + total_profit

    # الإحالات
    referrals = user.get("referrals", 0)
    referral_profit = user.get("referral_profit", 0)

    # عدد الأيام من أول دخول للبوت
    join_date = user.get("join_date")

    if join_date:
        days = (datetime.now() - join_date).days + 1
    else:
        days = 1

    await update.message.reply_text(
        f"""
━━━━━━━━━━━━━━━
        حسابي
━━━━━━━━━━━━━━━

• الرصيد: {balance:,} د.ع
• عدد الباقات: {packages_count}
• إجمالي رأس المال: {total_capital:,} د.ع
• إجمالي الأرباح: {total_profit:,} د.ع
• الإجمالي الكلي: {total_all:,} د.ع

━━━━━━━━━━━━━━━
        الإحالات
━━━━━━━━━━━━━━━

• عدد الإحالات: {referrals}
• أرباح الإحالة: {referral_profit:,} د.ع

━━━━━━━━━━━━━━━

• عدد الأيام: {days}

━━━━━━━━━━━━━━━
"""
    )



# =========================
# قسم الباقات
# =========================

PACKAGE_DAYS = 5
PROFIT_PER_10000 = 100


def get_package_amounts():
    amounts = list(range(10_000, 100_001, 10_000))
    amounts += list(range(150_000, 1_000_001, 50_000))
    amounts += list(range(1_500_000, 15_000_001, 500_000))
    return amounts


def packages_keyboard():
    amounts = get_package_amounts()
    keyboard = []

    for i in range(0, len(amounts), 2):
        row = []

        for amount in amounts[i:i + 2]:
            row.append(f"{amount:,} د.ع")

        keyboard.append(row)

    keyboard.append(["رجوع"])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def package_confirm_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["اشتراك"],
            ["العودة للباقات"]
        ],
        resize_keyboard=True
    )


async def packages(update, context):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if user.get("active_package"):
        await update.message.reply_text(
            "لديك باقة فعّالة حالياً، "
            "ولا يمكنك الاشتراك بباقة أخرى حتى تنتهي."
        )
        return

    context.user_data.pop("selected_package", None)

    await update.message.reply_text(
        "اختر قيمة الباقة:",
        reply_markup=packages_keyboard()
    )


async def package_details(update, context):
    text = update.message.text.strip()

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

    if amount not in get_package_amounts():
        return

    user_id = update.effective_user.id
    user = get_user(user_id)

    if user.get("active_package"):
        await update.message.reply_text(
            "لديك باقة فعّالة حالياً، "
            "ولا يمكنك الاشتراك بباقة أخرى حتى تنتهي."
        )
        return

    daily_profit = (amount // 10_000) * PROFIT_PER_10000
    total_profit = daily_profit * PACKAGE_DAYS

    context.user_data["selected_package"] = amount

    await update.message.reply_text(
        f"""━━━━━━━━━━━━━━━
        تفاصيل الباقة
━━━━━━━━━━━━━━━

• المبلغ: {amount:,} د.ع
• الربح اليومي: {daily_profit:,} د.ع
• المدة: {PACKAGE_DAYS} أيام
• يبدأ الربح من اليوم الثاني
• إجمالي الربح: {total_profit:,} د.ع

اضغط «اشتراك» للمتابعة.
━━━━━━━━━━━━━━━""",
        reply_markup=package_confirm_keyboard()
    )


async def package_confirm(update, context):
    user_id = update.effective_user.id
    user = get_user(user_id)

    amount = context.user_data.get("selected_package")

    if not amount:
        await update.message.reply_text(
            "يرجى اختيار الباقة أولاً."
        )
        return

    if user.get("active_package"):
        await update.message.reply_text(
            "لديك باقة فعّالة حالياً."
        )
        return

    balance = user.get("balance", 0)

    if balance < amount:
        await update.message.reply_text(
            f"""رصيدك غير كافٍ.

• قيمة الباقة: {amount:,} د.ع
• رصيدك الحالي: {balance:,} د.ع"""
        )
        return

    daily_profit = (amount // 10_000) * PROFIT_PER_10000
    total_profit = daily_profit * PACKAGE_DAYS
    now = datetime.now()

    # خصم الرصيد الداخلي للمحاكاة
    user["balance"] -= amount

    # تحديث عدد الباقات
    user["packages_count"] = (
        user.get("packages_count", 0) + 1
    )

    # تسجيل الباقة الحالية
    user["active_package"] = {
        "amount": amount,
        "daily_profit": daily_profit,
        "total_profit": total_profit,
        "days": PACKAGE_DAYS,
        "started_at": now,
        "profit_started_at": now + timedelta(days=1),
        "ends_at": now + timedelta(days=6),
        "profit_paid": 0,
        "status": "active"
    }

    context.user_data.pop("selected_package", None)

    await update.message.reply_text(
        f"""تم تفعيل الباقة بنجاح.

• المبلغ: {amount:,} د.ع
• الربح اليومي: {daily_profit:,} د.ع
• المدة: {PACKAGE_DAYS} أيام
• يبدأ الربح من اليوم الثاني

رصيدك الحالي:
{user["balance"]:,} د.ع""",
        reply_markup=user_keyboard(user_id)
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


# =========================
# إدارة المستخدمين - الأدمن
# =========================

async def admin_users(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    if not users:
        await update.message.reply_text(
            "لا يوجد مستخدمون حالياً."
        )
        return

    keyboard = []

    for user_id, user in users.items():
        name = user.get("name") or "بدون اسم"
        username = user.get("username") or "بدون يوزر"

        keyboard.append([
            InlineKeyboardButton(
                f"{name} | @{username}",
                callback_data=f"user_view:{user_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "رجوع",
            callback_data="admin_back"
        )
    ])

    await update.message.reply_text(
        "اختر المستخدم:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# تفاصيل المستخدم
# =========================

async def admin_user_view(update, context):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(query.data.split(":")[1])
    except (ValueError, IndexError):
        return

    user = users.get(user_id)

    if not user:
        await query.edit_message_text(
            "المستخدم غير موجود."
        )
        return

    name = user.get("name") or "بدون اسم"
    username = user.get("username") or "بدون يوزر"

    balance = user.get("balance", 0)
    packages_count = user.get("packages_count", 0)
    deposit_count = user.get("deposit_count", 0)
    total_capital = user.get("total_capital", 0)
    total_profit = user.get("total_profit", 0)
    profit_withdrawals = user.get("profit_withdrawals", 0)
    referrals = user.get("referrals", 0)
    referral_profit = user.get("referral_profit", 0)

    blocked = user.get("blocked", False)

    active_package = user.get("active_package")

    if active_package:
        package_amount = active_package.get("amount", 0)
        daily_profit = active_package.get("daily_profit", 0)
        status = active_package.get("status", "active")

        package_text = (
            f"المبلغ: {package_amount:,} د.ع\n"
            f"الربح اليومي: {daily_profit:,} د.ع\n"
            f"الحالة: {status}"
        )
    else:
        package_text = "لا توجد باقة فعّالة."

    status_text = "محظور" if blocked else "نشط"

    text = f"""
━━━━━━━━━━━━━━━
       بيانات المستخدم
━━━━━━━━━━━━━━━

• الاسم: {name}
• اليوزر: @{username}
• ID: {user_id}

• الرصيد: {balance:,} د.ع

• الباقة الحالية:
{package_text}

• مرات تفعيل الباقات: {packages_count}
• مرات الإيداع: {deposit_count}

• رأس المال:
{total_capital:,} د.ع

• الأرباح بدون رأس المال:
{total_profit:,} د.ع

• مرات استلام الأرباح:
{profit_withdrawals}

• الإجمالي مع رأس المال:
{total_capital + total_profit:,} د.ع

• عدد الإحالات:
{referrals}

• أرباح الإحالات:
{referral_profit:,} د.ع

• الحالة: {status_text}

━━━━━━━━━━━━━━━
"""

    if blocked:
        block_button = InlineKeyboardButton(
            "فك الحظر",
            callback_data=f"user_unblock:{user_id}"
        )
    else:
        block_button = InlineKeyboardButton(
            "حظر المستخدم",
            callback_data=f"user_block:{user_id}"
        )

    keyboard = [
        [
            InlineKeyboardButton(
                "إضافة رصيد نقاط",
                callback_data=f"add_points:{user_id}"
            ),
            InlineKeyboardButton(
                "خصم رصيد نقاط",
                callback_data=f"sub_points:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "تفاصيل الباقة",
                callback_data=f"user_package:{user_id}"
            )
        ],
        [
            block_button
        ],
        [
            InlineKeyboardButton(
                "رجوع للمستخدمين",
                callback_data="admin_users_back"
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# طلب مبلغ إضافة الرصيد
# =========================

async def admin_add_points(update, context):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.split(":")[1])

    context.user_data["balance_action"] = "add"
    context.user_data["balance_target"] = user_id

    await query.message.reply_text(
        "اكتب مقدار رصيد النقاط الذي تريد إضافته للمستخدم:"
    )


# =========================
# طلب مبلغ خصم الرصيد
# =========================

async def admin_sub_points(update, context):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.split(":")[1])

    context.user_data["balance_action"] = "sub"
    context.user_data["balance_target"] = user_id

    await query.message.reply_text(
        "اكتب مقدار رصيد النقاط الذي تريد خصمه من المستخدم:"
    )


# =========================
# تنفيذ إضافة / خصم الرصيد
# =========================

async def admin_balance_input(update, context):
    if update.effective_user.id != ADMIN_ID:
        return False

    action = context.user_data.get("balance_action")

    if not action:
        return False

    user_id = context.user_data.get("balance_target")

    if not user_id:
        context.user_data.pop("balance_action", None)
        context.user_data.pop("balance_target", None)
        return False

    user = users.get(user_id)

    if not user:
        await update.message.reply_text(
            "المستخدم غير موجود."
        )

        context.user_data.pop("balance_action", None)
        context.user_data.pop("balance_target", None)

        return True

    text = update.message.text.strip().replace(",", "")

    try:
        amount = int(text)
    except ValueError:
        await update.message.reply_text(
            "اكتب رقماً صحيحاً فقط."
        )
        return True

    if amount <= 0:
        await update.message.reply_text(
            "المبلغ لازم يكون أكبر من صفر."
        )
        return True

    current_balance = user.get("balance", 0)

    if action == "add":

        user["balance"] = current_balance + amount

        await update.message.reply_text(
            f"تمت إضافة {amount:,} د.ع إلى رصيد المستخدم.\n"
            f"الرصيد الجديد: {user['balance']:,} د.ع"
        )

    elif action == "sub":

        if amount > current_balance:
            await update.message.reply_text(
                f"رصيد المستخدم غير كافٍ للخصم.\n"
                f"الرصيد الحالي: {current_balance:,} د.ع"
            )
            return True

        user["balance"] = current_balance - amount

        await update.message.reply_text(
            f"تم خصم {amount:,} د.ع من رصيد المستخدم.\n"
            f"الرصيد الجديد: {user['balance']:,} د.ع"
        )

    context.user_data.pop("balance_action", None)
    context.user_data.pop("balance_target", None)

    return True


# =========================
# تفاصيل الباقة
# =========================

async def admin_user_package(update, context):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(query.data.split(":")[1])
    except (ValueError, IndexError):
        return

    user = users.get(user_id)

    if not user:
        return

    active_package = user.get("active_package")

    if not active_package:
        await query.edit_message_text(
            "لا توجد باقة فعّالة لهذا المستخدم.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "رجوع",
                        callback_data=f"user_view:{user_id}"
                    )
                ]
            ])
        )
        return

    amount = active_package.get("amount", 0)
    daily_profit = active_package.get("daily_profit", 0)
    total_profit = active_package.get("total_profit", 0)
    status = active_package.get("status", "active")

    started_at = active_package.get("started_at", "غير محدد")
    ends_at = active_package.get("ends_at", "غير محدد")

    text = f"""
━━━━━━━━━━━━━━━
       تفاصيل الباقة
━━━━━━━━━━━━━━━

• المبلغ: {amount:,} د.ع
• الربح اليومي: {daily_profit:,} د.ع
• إجمالي الربح: {total_profit:,} د.ع
• الحالة: {status}

• تاريخ التفعيل:
{started_at}

• تاريخ الانتهاء:
{ends_at}

━━━━━━━━━━━━━━━
"""

    keyboard = [[
        InlineKeyboardButton(
            "رجوع",
            callback_data=f"user_view:{user_id}"
        )
    ]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# حظر المستخدم
# =========================

async def admin_user_block(update, context):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.split(":")[1])

    user = users.get(user_id)

    if not user:
        return

    user["blocked"] = True

    await admin_user_view(update, context)


# =========================
# فك الحظر
# =========================

async def admin_user_unblock(update, context):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.split(":")[1])

    user = users.get(user_id)

    if not user:
        return

    user["blocked"] = False

    await admin_user_view(update, context)


# =========================
# الرجوع لقائمة المستخدمين
# =========================

async def admin_users_back(update, context):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    keyboard = []

    for user_id, user in users.items():

        name = user.get("name") or "بدون اسم"
        username = user.get("username") or "بدون يوزر"

        keyboard.append([
            InlineKeyboardButton(
                f"{name} | @{username}",
                callback_data=f"user_view:{user_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "رجوع",
            callback_data="admin_back"
        )
    ])

    await query.edit_message_text(
        "اختر المستخدم:",
        reply_markup=InlineKeyboardMarkup(keyboard)
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


    if await admin_balance_input(update, context):
        return
    
    # =========================
# ربط قسم الباقات
# =========================

    if text == "الباقات":
        await packages(update, context)
        return

    if text.endswith("د.ع"):
        await package_details(update, context)
        return

    if text == "اشتراك":
        await package_confirm(update, context)
        return

    if text == "العودة للباقات":
        await packages(update, context)
        return


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


# =========================
# تشغيل البوت
# =========================

app = Application.builder().token(TOKEN).build()


# =========================
# أمر /start
# =========================

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


# =========================
# أزرار المستخدمين - الأدمن
# =========================

app.add_handler(
    CallbackQueryHandler(
        admin_user_view,
        pattern=r"^user_view:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        admin_add_points,
        pattern=r"^add_points:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        admin_sub_points,
        pattern=r"^sub_points:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        admin_user_package,
        pattern=r"^user_package:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        admin_user_block,
        pattern=r"^user_block:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        admin_user_unblock,
        pattern=r"^user_unblock:"
    )
)

app.add_handler(
    CallbackQueryHandler(
        admin_users_back,
        pattern=r"^admin_users_back$"
    )
)


# =========================
# باقي أزرار البوت
# =========================

app.add_handler(
    CallbackQueryHandler(
        callback_handler
    )
)


# =========================
# الرسائل النصية
# =========================

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_router
    )
)


# =========================
# تشغيل البوت
# =========================

app.run_polling()
