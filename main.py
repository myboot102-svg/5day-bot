# -------- الاستيرادات --------
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# -------- المتغيرات --------
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8460661282

users = {}
states = {}
deposit_requests = []

deposit_numbers = {
    "زين كاش": "077XXXXXXXX",
    "سوبر كي": "077XXXXXXXX",
    "FIB": "077XXXXXXXX",
    "اسيا حوالة": "077XXXXXXXX",
    "USDT": "Txxxxxxxxx"
}

usdt_wallet = "0x66df098144E18aA2D8C95c9aeb333e78cD5D4992"

withdraw_requests = []

MIN_WITHDRAW = 8000
WITHDRAW_FEE = 1000


import time

PACKAGE_DAYS = 5      # مدة الباقة



# -------- دوال مساعدة --------

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "profit": 0,
            "package": None,
            "total_deposited": 0,
            "total_packages": 0,
            "join_date": int(time.time()),
            "ref_by": None,
            "referrals": 0,
            "referral_profit": 0,
            "first_deposit_done": False,
            "banned": False,
            "total_profit": 0
        }
    return users[user_id]


def set_state(context, state):
    context.user_data["state"] = state


def get_state(context):
    return context.user_data.get("state")


def clear_state(context):
    context.user_data["state"] = None


def update_user_profit(user):

    if not user.get("package") or not user["package"]["active"]:
        return

    now = int(time.time())
    start = user["package"]["start_time"]

    days_passed = (now - start) // 86400

    if days_passed <= 0:
        return

    payable_days = min(days_passed, PACKAGE_DAYS)

    already_paid = user["package"]["days_paid"]

    new_days = payable_days - already_paid

    if new_days <= 0:
        return

    amount = user["package"]["amount"]

    daily_profit = (amount // 10000) * 100

    profit = new_days * daily_profit

    user["balance"] += profit

    user["package"]["days_paid"] += new_days

    # انتهاء الباقة
    if user["package"]["days_paid"] >= PACKAGE_DAYS:

        user["balance"] += amount
        user["package"]["active"] = False

def main_menu(user_id):

    keyboard = [
        ["💰 الباقات الاستثمارية"],
        ["إيداع", "💸 سحب"],
        ["حسابي", "📊 حالة الاشتراك"],
        ["🔗 رابط الإحالة"]
    ]

    # 👑 زر الأدمن (يظهر بس للادمن)
    if user_id == ADMIN_ID:
        keyboard.append(["⚙️ لوحة الأدمن"])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def deposit_menu():
    keyboard = [[name] for name in deposit_numbers.keys()]
    keyboard.append(["رجوع"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def back_menu():
    return ReplyKeyboardMarkup([["رجوع"]], resize_keyboard=True)


# -------- الهاندل --------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    user = get_user(user_id)
    state = get_state(context)
    
    if user.get("banned"):
        await update.message.reply_text("🚫 انت محظور")
        return
    
    # ===== تحديث الأرباح =====

    if user["package"] and user["package"]["active"]:

        now = int(time.time())

        start_time = user["package"]["start_time"]
        

        # نحسب كم يوم مر (من بعد يوم التفعيل)
        days_passed = (now - start_time) // 86400

        # الربح يبدأ من اليوم الثاني
        if days_passed > 0:

            # كم يوم لازم ندفع له بعد
            days_to_pay = days_passed - user["package"]["days_paid"]

            if days_to_pay > 0:

                amount = user["package"]["amount"]

                daily_profit = (amount // 10000) * 100

                # نحسب الربح الكلي
                profit = daily_profit * days_to_pay

                # نضيفه
                user["balance"] += profit
                user["profit"] += profit

                user["total_profit"] += profit

                # نحدث الأيام
                user["package"]["days_paid"] += days_to_pay

                user["package"]["last_profit_time"] = now

        # ===== انتهاء الباقة =====
        if user["package"]["days_paid"] >= PACKAGE_DAYS and user["package"]["active"]:

            # رجوع رأس المال
            user["balance"] += user["package"]["amount"]

            # ايقاف الباقة
            user["package"]["active"] = False

    # ====== رسائل ======
    if update.message:

        text = update.message.text or ""

        # ===== ستارت =====
        if text.startswith("/start"):

            parts = text.split()

            referrer_id = None

            if len(parts) > 1:
                try:
                    referrer_id = int(parts[1])
                except:
                    referrer_id = None

            # ===== نظام الإحالة =====
            if referrer_id and referrer_id != user_id:

                if user["ref_by"] is None:

                    user["ref_by"] = referrer_id

                    ref_user = get_user(referrer_id)

                    ref_user["referrals"] += 1

                    # 💸 مكافأة التسجيل
                    ref_user["balance"] += 10
                    ref_user["referral_profit"] += 10

                    # 🔔 إشعار
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text="🎉 تم تسجيل شخص عن طريقك!\n💰 حصلت على 10 دينار"
                    )

            msg = """
            
أهلاً بك في بوت 5day للاستثمار الذكي

يسعدنا انضمامك إلينا، نحن نوفر لك منصة آمنة وموثوقة لنمو رأس مالك من خلال خطط استثمارية قصيرة الأمد.

تعريف برنامج الاستثمار:

مدة الاستثمار: 5 أيام فقط لكل دورة استثمارية
نظام الأرباح: تحصل على ربح 500 دينار لكل 10,000 دينار

الشروط والأحكام:

- يحق لكل مستخدم باقه واحده فقط
- يتم تجميد رأس المال لمدة 5 أيام
- يمكن سحب الأرباح يومياً
- يمكن التجديد بعد انتهاء الباقة
- تتحرر الأرباح مع رأس المال بعد انتهاء المدة


            """

            await update.message.reply_text(
                msg,
                reply_markup=main_menu(user_id)
            )

            return
    
        # ===== رجوع =====
        if text == "رجوع":

            clear_state(context)

            await update.message.reply_text(
                "رجعنا للقائمة الرئيسية",
                reply_markup=main_menu(user_id)
            )
            return

        # ===== حسابي =====
        
        elif text == "حسابي":

            now = int(time.time())

            days_since_join = (now - user["join_date"]) // 86400

            balance = user["balance"]
            total_packages = user["total_packages"]
            total_deposit = user["total_deposit"]
            total_profit = user["total_profit"]

            referrals = user["referrals"]
            referral_profit = user["referral_profit"]

            # 🔥 الإجمالي الكلي
            total_all = total_deposit + total_profit

            msg = f"""
━━━━━━━━━━━━━━━
        حسابي
━━━━━━━━━━━━━━━

• الرصيد: {balance}

• عدد الباقات: {total_packages}
• إجمالي رأس المال: {total_deposit}
• إجمالي الأرباح: {total_profit}
• الإجمالي الكلي: {total_all}

━━━━━━━━━━━━━━━

        الإحالات
• عدد الإحالات: {referrals}
• أرباح الإحالة: {referral_profit}

━━━━━━━━━━━━━━━

• عدد الأيام: {days_since_join}

━━━━━━━━━━━━━━━
            """

            await update.message.reply_text(msg)
            return

        #----- الباقات الاستثماريه --=====
        
        elif text == "💰 الباقات الاستثمارية":

            msg = "اختر مبلغ الاستثمار :"

            kb = [
                ["10،000", "20،000", "30،000"],
                ["40،000", "50،000", "60،000"],
                ["70،000", "80،000", "90،000"],
                ["100،000", "200،000", "300،000"],
                ["400،000", "500،000", "600،000"],
                ["700،000", "800،000", "900،000"],
                ["1،000،000"],
                ["رجوع"]
            ]

            await update.message.reply_text(
                msg,
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
            )

            set_state(context, "choose_package")
            return
    
    
        #------- اختيار الباقه------
        
        elif get_state(context) == "choose_package":

            if text == "رجوع":
                await update.message.reply_text("رجعنا", reply_markup=main_menu(user_id))
                clear_state(context)
                return

            # تنظيف الرقم (حتى يدعم 10،000)
            clean_text = text.replace("،", "").replace(",", "")

            if not clean_text.isdigit():
                return

            amount = int(clean_text)

            if amount < 10000 or amount > 1000000 or amount % 10000 != 0:
                await update.message.reply_text("اختار مبلغ صحيح")
                return

            # الربح اليومي
            daily_profit = (amount // 10000) * 100

            msg = f"""
- تفاصيل الباقة :

المبلغ: {amount}
الربح اليومي: {daily_profit}
المدة: {PACKAGE_DAYS} أيام

- يبدأ الربح من اليوم الثاني
- يتم استرجاع رأس المال بالكامل تلقائياً بعد انتهاء مدة التفعيل
            """

            kb = [["تأكيد"], ["رجوع"]]

            # حفظ المبلغ
            context.user_data["package_amount"] = amount

            await update.message.reply_text(
                msg,
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
            )

            set_state(context, "confirm_package")
            return
    
    
        #------- تنفيذ الشراء ------
        
        elif get_state(context) == "confirm_package" and text == "تأكيد":

            if user.get("package") and user["package"].get("active"):

                await update.message.reply_text(
                    "❌ لديك باقة مفعلة حالياً\n⏳ انتظر حتى تنتهي ثم يمكنك شراء باقة جديدة"
                )
                return

            amount = context.user_data.get("package_amount")

            if user["balance"] < amount:
                await update.message.reply_text("رصيدك غير كافي ❌")
                return

            # خصم الرصيد
            user["balance"] -= amount

            user["total_packages"] += 1

            # تفعيل الباقة
            user["package"] = {
                "amount": amount,
                "start_time": int(time.time()),
                "last_profit_time": int(time.time()),
                "days_paid": 0,
                "active": True
            }


            if user.get("ref_by") and not user["first_deposit_done"]:

                ref_user = get_user(user["ref_by"])

                bonus = (amount // 10000) * 100

                ref_user["balance"] += bonus
                ref_user["referral_profit"] += bonus

                # نمنع التكرار
                user["first_deposit_done"] = True
                
                # 🔔 إشعار
                await context.bot.send_message(
                    chat_id=user["ref_by"],
                    text=f"🎉 صديقك فعل باقة!\n💰 حصلت على {bonus} دينار"
                )

            await update.message.reply_text("تم تفعيل الباقة ✅")

            clear_state(context)
            return
    
    
    
        #------- حالة الاشتراك --------
        if text == "📊 حالة الاشتراك":

            package = user.get("package")

            if not package or not package.get("active"):
                await update.message.reply_text("ما عندك اشتراك حالياً ❌")
                return

            amount = package["amount"]
            days_paid = package["days_paid"]

            daily_profit = (amount // 10000) * 100

            remaining_days = PACKAGE_DAYS - days_paid

            total_profit = daily_profit * days_paid

            msg = f"""
📊 حالة الاشتراك

💰 قيمة الباقة: {amount}
📈 الربح اليومي: {daily_profit}

📅 الأيام المدفوعة: {days_paid}
⏳ الأيام المتبقية: {remaining_days}

💵 إجمالي الأرباح: {total_profit}
            """

            await update.message.reply_text(msg)
            return
    
    
        #------- رابط الاحاله -------
        elif text == "🔗 رابط الإحالة":

            bot_username = "daay5_bot"

            link = f"https://t.me/{bot_username}?start={user_id}"

            msg = f"""
🔗 رابط الإحالة الخاص بك:

{link}

📌 شاركه واربح:
• 10 دينار لكل تسجيل
• 100 دينار لكل 10,000 أول باقة
            """

            await update.message.reply_text(msg)
            return
    
    
    
        #========= الايداع=======
        elif text == "إيداع" and state is None:

            msg = """
⚠️ تنبيه

تأكد من التحويل الصحيح قبل إرسال الطلب.

الإدارة غير مسؤولة عن أي خطأ في الرقم أو المبلغ.

اضغط موافق للمتابعة
            """

            kb = [
                ["✅ موافق"],
                ["رجوع"]
            ]

            await update.message.reply_text(
                msg,
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
            )

            set_state(context, "deposit_warning")
            return
  
  
        #------ بعد الموافقه اختيار المحفظه ---
        elif get_state(context) == "deposit_warning":

            if text == "رجوع":
                await update.message.reply_text(
                    "تم الإلغاء",
                    reply_markup=main_menu(user_id)
                )
                clear_state(context)
                return

            if text == "✅ موافق":

                kb = [
                    ["زين كاش", "سوبر كي"],
                    ["FIB", "اسيا حوالة"],
                    ["اسيا كارد", "زين (اثير)"],
                    ["USDT"],
                    ["رجوع"]
                ]

                await update.message.reply_text(
                    "اختر المحفظة",
                    reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
                )

                set_state(context, "deposit_wallet")
                return
  

        #---- اختار المحفظه-----
        elif get_state(context) == "deposit_wallet":

            if text == "رجوع":
                await update.message.reply_text(
                    "رجعنا للقائمة",
                    reply_markup=main_menu(user_id)
                )
                clear_state(context)
                return

            context.user_data["wallet"] = text


        #----- محافظ عاديه-----
        if get_state(context) == "deposit_wallet" and text in deposit_numbers:

            await update.message.reply_text("اكتب مبلغ الإيداع")

            set_state(context, "deposit_amount")
            return


        #----- محافظ الكارت-----
        elif text in ["اسيا كارد", "زين (اثير)"]:

            await update.message.reply_text("اكتب مبلغ الكارت")

            set_state(context, "card_amount")
            return


        #------ محافظ يو اس دي------
        elif text == "USDT":

            msg = f"""
قم بالتحويل على شبكة TRC20

العنوان:

{usdt_wallet}

ثم ارسل سكرين التحويل
            """

            await update.message.reply_text(msg)

            set_state(context, "usdt_image")
            return


        #----- كتابة مبلغ المحفظه العاديه-------
        elif get_state(context) == "deposit_amount":

            context.user_data["amount"] = text

            await update.message.reply_text("اكتب اسم المرسل")

            set_state(context, "deposit_name")
            return


        #----- اسم المرسل------
        elif get_state(context) == "deposit_name":

            context.user_data["name"] = text

            await update.message.reply_text("اكتب رقم المرسل")

            set_state(context, "deposit_sender")
            return


        #---- رقم المرسل واضهار رقم التحويل------
        elif get_state(context) == "deposit_sender":

            context.user_data["sender"] = text

            wallet = context.user_data["wallet"]

            number = deposit_numbers[wallet]

            msg = f"""
قم بالتحويل على الرقم التالي خلال 10 دقائق

{number}

ثم ارسل سكرين التحويل
            """

            await update.message.reply_text(msg)

            set_state(context, "deposit_image")
            return


        #------ نظام الكارت الكوود---------
        elif get_state(context) == "card_amount":

            context.user_data["amount"] = text

            await update.message.reply_text("ارسل كود الكارت")

            set_state(context, "card_code")
            return


        #----- كود الكارت------
        elif get_state(context) == "card_code":

            context.user_data["code"] = text

            await update.message.reply_text("ارسل صورة الكارت")

            set_state(context, "card_image")
            return

        #شرط الصور--------------
        if update.message.photo:

            state = get_state(context)

            if state in ["deposit_image", "card_image", "usdt_image"]:

                photo = update.message.photo[-1].file_id
                context.user_data["photo"] = photo

                msg = f"""
📋 تأكيد معلومات الإيداع

💳 الطريقة: {context.user_data.get("wallet")}

💰 المبلغ: {context.user_data.get("amount")}

👤 الاسم: {context.user_data.get("name","-")}

📱 الرقم: {context.user_data.get("sender","-")}

هل تريد إرسال الطلب؟
                """

                sent = await update.message.reply_photo(
                    photo=photo,
                    caption=msg,
                    reply_markup=ReplyKeyboardMarkup(
                        [["✅ تأكيد الإرسال"], ["رجوع"]],
                        resize_keyboard=True
                    )
                )

                context.user_data["confirm_msg_id"] = sent.message_id
                context.user_data["confirm_chat"] = update.effective_chat.id

                set_state(context, "deposit_confirm")

                return

        #-------التاكيد----
        elif get_state(context) == "deposit_confirm":

            if text == "رجوع":

                await update.message.reply_text(
                    "تم إلغاء الطلب",
                    reply_markup=main_menu(user_id)
                )

                clear_state(context)
                return


            if text == "✅ تأكيد الإرسال":

                # حذف رسالة المعلومات والصورة
                try:
                    await context.bot.delete_message(
                        chat_id=context.user_data["confirm_chat"],
                        message_id=context.user_data["confirm_msg_id"]
                    )
                except:
                    pass

                # حذف رسالة زر التأكيد
                try:
                    await update.message.delete()
                except:
                    pass


                # حفظ الطلب
                req_id = len(deposit_requests)

                deposit_requests.append({
                    "id": req_id,
                    "user_id": user_id,
                    "wallet": context.user_data.get("wallet"),
                    "amount": context.user_data.get("amount"),
                    "name": context.user_data.get("name"),
                    "sender": context.user_data.get("sender"),
                    "photo": context.user_data.get("photo")
                })  


                await update.message.reply_text(
                    "✅ تم ارسال طلب الإيداع\n⏳ جاري المعالجة (1 - 2 ساعة)",
                    reply_markup=main_menu(user_id)
                )

                clear_state(context)
                return


        #========= السحب======

        elif text == "💸 سحب":

            msg = """
⚠️ تنبيه

تأكد من إدخال معلوماتك بشكل صحيح.

الإدارة غير مسؤولة عن أي خطأ.

هل تريد المتابعة؟
            """

            kb = [["✅ موافق"], ["رجوع"]]

            await update.message.reply_text(
                msg,
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
            )

            set_state(context, "withdraw_warning")
            return


        #------- بعد الموافقه ----
        elif get_state(context) == "withdraw_warning":

            if text == "رجوع":
                clear_state(context)
                await update.message.reply_text("تم الإلغاء", reply_markup=main_menu(user_id))
                return

            if text == "✅ موافق":

                await update.message.reply_text("💰 اكتب مبلغ السحب")

                set_state(context, "withdraw_amount")
                return

        
        #------- المبلغ و العموله ----
        elif get_state(context) == "withdraw_amount":

            if not text.isdigit():
                await update.message.reply_text("اكتب رقم صحيح")
                return

            amount = int(text)

            if amount < MIN_WITHDRAW:
                await update.message.reply_text(f"❌ الحد الأدنى للسحب {MIN_WITHDRAW}")
                return

            total = amount + WITHDRAW_FEE

            if total > user["balance"]:
                await update.message.reply_text(f"رصيدك غير كافي ❌\nالمطلوب: {total}")
                return

            context.user_data["amount"] = amount
            context.user_data["total"] = total

            kb = [
                ["زين كاش.", "سوبر كي."],
                ["FIB.", "اسيا حوالة."],
                ["USDT."],
                ["رجوع"]
            ]

            await update.message.reply_text(
                f"""
💰 تفاصيل السحب

المبلغ: {amount}
العمولة: {WITHDRAW_FEE}
الصافي: {amount - WITHDRAW_FEE}

اختر الطريقة
                """,
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
            )

            set_state(context, "withdraw_method")
            return


        #-------- الطريقه ------
        elif get_state(context) == "withdraw_method":

            if text == "رجوع":
                clear_state(context)
                await update.message.reply_text("تم الإلغاء", reply_markup=main_menu(user_id))
                return

            context.user_data["method"] = text

            await update.message.reply_text("👤 اكتب الاسم")

            set_state(context, "withdraw_name")
            return


        #------ الاسم-----
        elif get_state(context) == "withdraw_name":

            context.user_data["name"] = text

            await update.message.reply_text("📱 اكتب الرقم أو العنوان")

            set_state(context, "withdraw_number")
            return

        #----- الرقم -----
        elif get_state(context) == "withdraw_number":

            context.user_data["number"] = text

            await update.message.reply_text("📷 ارسل الباركود")

            set_state(context, "withdraw_barcode")
            return

        #------- باركود و تاكيد ------
        if update.message.photo and get_state(context) == "withdraw_barcode":

            photo = update.message.photo[-1].file_id
            context.user_data["photo"] = photo

            msg = f"""
📋 تأكيد السحب

💰 {context.user_data["amount"]}
💸 العمولة: {WITHDRAW_FEE}
📥 الصافي: {context.user_data["amount"] - WITHDRAW_FEE}

💳 {context.user_data["method"]}
👤 {context.user_data["name"]}
📱 {context.user_data["number"]}

تأكيد؟
            """

            sent = await update.message.reply_photo(
                photo=photo,
                caption=msg,
                reply_markup=ReplyKeyboardMarkup(
                    [["✅ تأكيد السحب"], ["رجوع"]],
                    resize_keyboard=True
                )
            )

            context.user_data["confirm_msg_id"] = sent.message_id

            set_state(context, "withdraw_confirm")
            return

        #----- تاكيد السحب ----
        elif get_state(context) == "withdraw_confirm":

            if text == "رجوع":
                clear_state(context)
                await update.message.reply_text("تم الإلغاء", reply_markup=main_menu(user_id))
                return


            if text == "✅ تأكيد السحب":

                # حذف رسالة التأكيد
                try:
                    await context.bot.delete_message(
                        chat_id=user_id,
                        message_id=context.user_data["confirm_msg_id"]
                    )
                except:
                    pass

                user["balance"] -= context.user_data["amount"]

                req_id = len(withdraw_requests)

                withdraw_requests.append({
                    "id": req_id,
                    "user_id": user_id,
                    "amount": context.user_data["amount"],
                    "method": context.user_data["method"],
                    "name": context.user_data["name"],
                    "number": context.user_data["number"],
                    "photo": context.user_data["photo"]
                })

                await update.message.reply_text(
                    "📥 تم استلام طلب السحب\n🔄 الطلب قيد المراجعة حالياً\n⏳ سيتم إتمام المعالجة خلال 24 ساعة كحد أقصى",
                    reply_markup=main_menu(user_id)
                )

                clear_state(context)
                return



        #------- لوحة الادمن -------
        
        elif text == "⚙️ لوحة الأدمن" and user_id == ADMIN_ID:

            kb = [
                ["🔍 بحث عن مستخدم"],
                ["📥 طلبات الإيداع", "📤 طلبات السحب"],
                ["💳 تغيير أرقام المحافظ"],
                ["📢 رسالة جماعية"],
                ["رجوع"]
            ]

            await update.message.reply_text(
                "👑 لوحة الأدمن",
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
            )

            set_state(context, "admin_panel")
            return
        
        
        
        #------ بحث عن مستخدم ----

        elif text == "🔍 بحث عن مستخدم":
            await update.message.reply_text("ارسل ID المستخدم")
            set_state(context, "admin_search")
            return
        
        #------- ايدي وعرض ------
        
        elif get_state(context) == "admin_search":

            if not text.isdigit():
                await update.message.reply_text("ارسل ID صحيح")
                return

            target_id = int(text)

            if target_id not in users:
                await update.message.reply_text("المستخدم غير موجود")
                return

            target = users[target_id]

            package = target.get("package")

            if package and package.get("active"):
                package_text = f"مفعل ({package['amount']})"
            else:
                package_text = "لا يوجد"

            msg = f"""
👤 معلومات المستخدم

🆔 ID: {target_id}

💰 الرصيد: {target["balance"]}
📈 الأرباح: {target["profit"]}
📦 الباقة: {package_text}
            """

            kb = [
                ["➕ إضافة رصيد", "➖ خصم رصيد"],
                ["🚫 حظر", "✅ فك حظر"],
                ["📦 تفاصيل الباقة"],
                ["رجوع"]
            ]

            context.user_data["target_id"] = target_id

            await update.message.reply_text(
                msg,
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
            )

            set_state(context, "admin_actions")
            return


        #------ تفاصيل الباقه -----
        elif get_state(context) == "admin_actions" and text == "📦 تفاصيل الباقة":

            target_id = context.user_data["target_id"]
            target = users[target_id]

            package = target.get("package")

            if not package or not package.get("active"):
                await update.message.reply_text("ما عنده باقة حالياً")
                return

            msg = f"""
📦 تفاصيل الباقة

💰 المبلغ: {package["amount"]}
📅 الأيام المدفوعة: {package["days_paid"]}
⏳ الحالة: مفعلة
            """

            await update.message.reply_text(msg)
            return


        #--------- اضافة رصيد -----
        elif get_state(context) == "admin_actions" and text == "➕ إضافة رصيد":

            await update.message.reply_text("اكتب المبلغ")
            set_state(context, "admin_add")
            return


        elif get_state(context) == "admin_add":

            if not text.isdigit():
                return

            amount = int(text)

            target_id = context.user_data["target_id"]

            users[target_id]["balance"] += amount

            await update.message.reply_text("تمت الإضافة ✅")

            clear_state(context)
            return


        #------- خصم الرصيد -----
        elif get_state(context) == "admin_actions" and text == "➖ خصم رصيد":

            await update.message.reply_text("اكتب المبلغ")
            set_state(context, "admin_sub")
            return


        elif get_state(context) == "admin_sub":

            if not text.isdigit():
                return

            amount = int(text)

            target_id = context.user_data["target_id"]

            users[target_id]["balance"] -= amount

            await update.message.reply_text("تم الخصم ✅")

            clear_state(context)
            return


        #-------- الحظر ------
        elif get_state(context) == "admin_actions" and text == "🚫 حظر":

            target_id = context.user_data["target_id"]

            users[target_id]["banned"] = True

            await update.message.reply_text("تم الحظر 🚫")

            clear_state(context)
            return


        #------ فك الحظر ------
        elif get_state(context) == "admin_actions" and text == "✅ فك حظر":

            target_id = context.user_data["target_id"]

            users[target_id]["banned"] = False

            await update.message.reply_text("تم فك الحظر ✅")

            clear_state(context)
            return



        #------- تفير المحافط -----
        elif text == "💳 تغيير أرقام المحافظ" and user_id == ADMIN_ID:

            kb = [
                ["زين كاش", "سوبر كي"],
                ["FIB", "اسيا حوالة"],
                ["USDT"],
                ["رجوع"]
            ]

            await update.message.reply_text(
                "👇 اختر المحفظة للتعديل",
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
            )

            set_state(context, "admin_edit_wallet")
            return

        #------- اختيار المحفظه -----
        elif get_state(context) == "admin_edit_wallet" and user_id == ADMIN_ID:

            if text == "رجوع":
                clear_state(context)
                await update.message.reply_text(
                    "رجعنا للقائمة",
                    reply_markup=main_menu(user_id)
                )
                return

            if text not in deposit_numbers:
                return

            context.user_data["wallet_name"] = text

            await update.message.reply_text(
                f"✏️ ارسل الرقم الجديد لـ {text}"
            )

            set_state(context, "admin_edit_wallet_value")
            return

        #-------- حفظ الرقم -----
        elif get_state(context) == "admin_edit_wallet_value" and user_id == ADMIN_ID:

            wallet = context.user_data.get("wallet_name")

            if not wallet:
                clear_state(context)
                return

            deposit_numbers[wallet] = text

            await update.message.reply_text(
                f"✅ تم تحديث {wallet}\n\n📌 الرقم الجديد:\n{text}",
                reply_markup=main_menu(user_id)
            )

            clear_state(context)
            return


        #----- رساله جماعيه -----
        elif text == "📢 رسالة جماعية" and user_id == ADMIN_ID:

            await update.message.reply_text("✉️ ارسل الرسالة (نص أو صورة)")

            set_state(context, "admin_broadcast")
            return


        #----- استقبال النص ----
        elif get_state(context) == "admin_broadcast" and user_id == ADMIN_ID:

            sent = 0
            failed = 0

            for uid in users:

                try:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=text
                    )
                    sent += 1
                except:
                    failed += 1

                await update.message.reply_text(
                    f"✅ تم الإرسال\n\n📤 وصل: {sent}\n❌ فشل: {failed}"
                )

                clear_state(context)
                return


        #------ صوره ----
        if update.message.photo and get_state(context) == "admin_broadcast":

            photo = update.message.photo[-1].file_id
            caption = update.message.caption if update.message.caption else ""

            sent = 0
            failed = 0

            for uid in users:

                try:
                    await context.bot.send_photo(
                        chat_id=uid,
                        photo=photo,
                        caption=caption
                    )
                    sent += 1
                except:
                    failed += 1

                    await update.message.reply_text(
                        f"✅ تم الإرسال\n\n📤 وصل: {sent}\n❌ فشل: {failed}"
                    )

                clear_state(context)
                return


        #------ طلبات الايداع
        
        
        elif text == "📥 طلبات الإيداع" and user_id == ADMIN_ID:
            
            if not deposit_requests:

                await update.message.reply_text("لا يوجد طلبات حالياً")
                return


            for req in deposit_requests:

                msg = f"""
📥 طلب إيداع

👤 ID : {req["user_id"]}

💳 المحفظة : {req["wallet"]}

💰 المبلغ : {req["amount"]}

👤 الاسم : {req["name"]}

📱 الرقم : {req["sender"]}
                """

                kb = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                        "✅ قبول",
                        callback_data=f"deposit_accept_{req['id']}"
                        ),
                        InlineKeyboardButton(
                        "❌ رفض",
                        callback_data=f"deposit_reject_{req['id']}"
                        )
                    ]
                ])

                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=req["photo"],
                    caption=msg,
                    reply_markup=kb
                )
    
        #===== طلبات السحب =====
        elif text == "📤 طلبات السحب" and user_id == ADMIN_ID:

            if not withdraw_requests:
                await update.message.reply_text("لا يوجد طلبات")
                return

            for req in withdraw_requests:

                msg = f"""
📤 طلب سحب

👤 {req["user_id"]}

💰 {req["amount"]}
💸 {WITHDRAW_FEE}
📥 {req["amount"] - WITHDRAW_FEE}

💳 {req["method"]}
👤 {req["name"]}
📱 {req["number"]}
                """

                kb = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ قبول", callback_data=f"w_acc_{req['id']}"),
                        InlineKeyboardButton("❌ رفض", callback_data=f"w_rej_{req['id']}")
                    ]
                ])

                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=req["photo"],
                    caption=msg,
                    reply_markup=kb
                )
    
    
    # ====== الأزرار الشفافة ======
    elif update.callback_query:

        query = update.callback_query
        data = query.data

        await query.answer()

        #----- قبول-----
        
        if data.startswith("deposit_accept_"):

            req_id = int(data.split("_")[2])

            req = next((r for r in deposit_requests if r["id"] == req_id), None)

            if not req:
                await query.answer("الطلب غير موجود", show_alert=True)
                return

            user = get_user(req["user_id"])

            user["balance"] += int(req["amount"])

            user["total_deposit"] += int(req["amount"])

            deposit_requests.remove(req)

            await query.edit_message_caption(
                caption="✅ تم قبول الطلب وإضافة الرصيد"
            )

            await context.bot.send_message(
                chat_id=req["user_id"],
                text=f"✅ تم قبول إيداعك\nتم إضافة {req['amount']} إلى رصيدك"
            )
    
    
        #------ رفض-----
        elif data.startswith("deposit_reject_"):

            req_id = int(data.split("_")[2])

            req = next((r for r in deposit_requests if r["id"] == req_id), None)

            if not req:
                await query.answer("الطلب غير موجود", show_alert=True)
                return

            deposit_requests.remove(req)

            await query.edit_message_caption(
                caption="❌ تم رفض الطلب"
            )

            await context.bot.send_message(
                chat_id=req["user_id"],
                text="❌ تم رفض طلب الإيداع"
            )



        #====== قبول السحب =====
        if data.startswith("w_acc_"):

            req_id = int(data.split("_")[2])
            req = next(r for r in withdraw_requests if r["id"] == req_id)

            withdraw_requests.remove(req)

            await query.edit_message_caption("✅ تم القبول")

            net = req["amount"] - WITHDRAW_FEE

            await context.bot.send_message(
                chat_id=req["user_id"],
                text=f"✅ تم تحويل {net} دينار"
            )

        #------- رفض السحب ---
        elif data.startswith("w_rej_"):

            req_id = int(data.split("_")[2])
            req = next(r for r in withdraw_requests if r["id"] == req_id)

            user = get_user(req["user_id"])
            user["balance"] += req["amount"]

            withdraw_requests.remove(req)

            await query.edit_message_caption("❌ تم الرفض")

            await context.bot.send_message(
                chat_id=req["user_id"],
                text=f"❌ تم رفض الطلب\nتم إعادة {req['amount']} دينار"
            )
        


# -------- تشغيل --------
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.ALL, handle))
app.add_handler(CallbackQueryHandler(handle))

print("Bot Started...")

app.run_polling()
