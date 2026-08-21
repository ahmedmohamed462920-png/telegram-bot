import json
import os
import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

# --- الإعدادات الأساسية للبوت ---
TOKEN = "8942289190:AAFaylYUr3ySiUUCntptfXdTz8TcFCM7JRs"
ADMIN_ID = 8697852304
CHANNEL_ID = -1003931541362
CHANNEL_USERNAME = "Jsoxkedoaoejf"
SUPPORT_USERNAME = "AHMED1_mo600"
SMM_API_URL = "https://igcpanel.com/api/v2"
SMM_API_KEY = "3d5b4555b8c244318fbec23902de49d2"
VODAFONE_WALLET = "01018729516"
WALLET_NAME = "AHMED"

BALANCES_FILE = "user_balances.json"
ORDERS_FILE = "user_orders.json"
REFERRALS_FILE = "user_referrals.json"
FAVS_FILE = "user_favorites.json"

logging.basicConfig(level=logging.INFO)
cached_categories = {}
free_services = {} 
user_states = {}    
category_mapping = {}

def load_json_file(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"خطأ في قراءة الملف {filename}: {e}")
    return default_val

def save_json_file(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في حفظ الملف {filename}: {e}")

user_balances = {int(k): float(v) for k, v in load_json_file(BALANCES_FILE, {}).items()}
user_orders = {int(k): v for k, v in load_json_file(ORDERS_FILE, {}).items()}
referrals_data = {int(k): v for k, v in load_json_file(REFERRALS_FILE, {}).items()}
user_favorites = {int(k): v for k, v in load_json_file(FAVS_FILE, {}).items()}

def save_balances():
    save_json_file(BALANCES_FILE, user_balances)

def save_orders_data():
    save_json_file(ORDERS_FILE, user_orders)

def save_referrals_data():
    save_json_file(REFERRALS_FILE, referrals_data)

def save_favorites_data():
    save_json_file(FAVS_FILE, user_favorites)

def check_site_balance():
    try:
        response = requests.post(SMM_API_URL, data={"key": SMM_API_KEY, "action": "balance"}, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            balance = float(res_data.get("balance", res_data.get("cash", 0.0)))
            return balance
    except Exception as e:
        print(f"خطأ أثناء التحقق من رصيد الموقع: {e}")
    return 0.0 

def get_service_sort_priority(service_name):
    name = service_name.lower()
    if "مشتركين" in name or "subscribers" in name or "subscriber" in name:
        return 0 
    elif "متابعين" in name or "followers" in name or "follower" in name:
        return 1
    elif "لايك" in name or "likes" in name or "like" in name:
        return 2
    elif "مشاهدات" in name or "views" in name or "view" in name:
        return 3
    elif "تعليق" in name or "comments" in name or "comment" in name:
        return 4
    return 5

def load_services():
    global cached_categories, free_services, category_mapping
    try:
        response = requests.post(SMM_API_URL, data={"key": SMM_API_KEY, "action": "services"}, timeout=15)
        if response.status_code == 200:
            services_list = response.json()
            temp = {}
            temp_free = []
            category_mapping.clear()
            cat_index = 0
            
            for s in services_list:
                cat = s.get("category", "خدمات أخرى").strip()
                s_name_lower = s.get("name", "").lower()
                cat_lower = cat.lower()
                
                try:
                    original_rate = float(s.get("rate", 0))
                except:
                    original_rate = 0.0

                if "مجاني" in cat_lower or "free" in cat_lower or "مجاني" in s_name_lower or "free" in s_name_lower or original_rate == 0:
                    temp_free.append(s)

                if cat not in temp: 
                    temp[cat] = []
                    cat_index += 1
                    category_mapping[str(cat_index)] = cat
                
                base_price = original_rate * 50  
                s["api_rate"] = base_price          
                s["client_rate"] = base_price * 1.5   
                
                temp[cat].append(s)
            
            for cat in temp:
                temp[cat].sort(key=lambda x: get_service_sort_priority(x.get("name", "")))
                
            cached_categories = temp
            free_services = temp_free
    except Exception as e:
        print(f"خطأ في تحميل الخدمات: {e}")

def get_main_menu_keyboard():
    return [
        [InlineKeyboardButton("🚀 خدمات رشق السوشيال ميديا", callback_data="show_categories")],
        [InlineKeyboardButton("🔍 بحث سريع عن خدمة", callback_data="search_service_prompt")],
        [InlineKeyboardButton("⭐ خدماتي المفضلة", callback_data="my_favorites")],
        [InlineKeyboardButton("🎁 الرشق اليومي المجاني", callback_data="free_section")],
        [InlineKeyboardButton("📦 طلباتي السابقة وحالتها", callback_data="my_orders")],
        [InlineKeyboardButton("👥 دعوة أصدقاء (اربح رصيد)", callback_data="referral_program")],
        [InlineKeyboardButton("💳 شحن الرصيد (فودافون كاش)", callback_data="vodafone_info")],
        [InlineKeyboardButton("👤 حسابي", callback_data="my_account")],
        [InlineKeyboardButton("💬 تواصل مع الدعم", url=f"https://t.me/{SUPPORT_USERNAME}")]
    ]

def get_admin_menu_keyboard():
    return [
        [InlineKeyboardButton("💰 إضافة رصيد لمستخدم", callback_data="admin_add_balance")],
        [InlineKeyboardButton("➖ خصم رصيد من مستخدم", callback_data="admin_sub_balance")],
        [InlineKeyboardButton("👥 إحصائيات البوت", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
    ]

async def check_user_subscription(user_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك: {e}")
    return False

async def update_user_orders_status(user_id, context, update_obj=None):
    if user_id not in user_orders or not user_orders[user_id]:
        return
    
    recent_orders = user_orders[user_id]
    
    client_name = "مستخدم تيليجرام"
    if update_obj and update_obj.effective_user:
        if update_obj.effective_user.first_name:
            client_name = update_obj.effective_user.first_name
    else:
        try:
            chat_user = await context.bot.get_chat(user_id)
            if chat_user.first_name:
                client_name = chat_user.first_name
        except:
            pass

    for o in recent_orders:
        old_status = str(o.get("status", "")).strip().lower()
        if old_status in ["completed", "complete", "success", "canceled", "partial"]:
            continue
            
        o_id = str(o["order_id"])
        try:
            payload = {
                "key": SMM_API_KEY,
                "action": "status",
                "order": o_id
            }
            res = requests.post(SMM_API_URL, data=payload, timeout=10).json()
            
            if isinstance(res, dict):
                site_status = str(res.get("status", "")).strip().lower()
                if not site_status:
                    site_status = str(res.get("order_status", "")).strip().lower()
                
                if site_status in ["completed", "complete", "success"]:
                    o["status"] = "Completed"
                    save_orders_data()
                    
                    success_msg = (
                        f"✅ اكتمل طلبك بنجاح!\n"
                        f"🔢 رقم الطلب: {o_id}\n"
                        f"📦 الخدمة: {o.get('service_name', 'خدمة سوشيال ميديا')}\n"
                        f"📊 الكمية: {o.get('qty')}\n"
                        f"🔗 الرابط: {o.get('link')}"
                    )
                    try:
                        await context.bot.send_message(chat_id=user_id, text=success_msg, parse_mode="Markdown")
                    except:
                        pass

                    channel_proof_msg = (
                        f"⭐ **تم التسليم بنجاح** ⭐\n\n"
                        f"👑 **اسم العميل:** `{client_name}`\n"
                        f"💎 **الخدمة:** {o.get('service_name', 'خدمة سوشيال ميديا')}\n"
                        f"🔥 **العدد:** {o.get('qty')}\n"
                        f"💸 **المبلغ:** {o.get('total_cost', 0)} جنيه\n"
                        f"🛡 **الحالة:** تم التسليم ✅\n\n"
                        f"🎁 **شكراً لثقتك بنا – L.G ❤️**"
                    )
                    try:
                        await context.bot.send_message(chat_id=CHANNEL_ID, text=channel_proof_msg, parse_mode="Markdown")
                    except Exception as channel_err:
                        print(f"خطأ في إرسال الإثبات للقناة: {channel_err}")
                elif site_status:
                    o["status"] = site_status.capitalize()
                    save_orders_data()
        except Exception as e:
            print(f"خطأ في فحص حالة الطلب {o_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    args = context.args
    if args and args[0].startswith("ref_"):
        try:
            inviter_id = int(args[0].replace("ref_", ""))
            if inviter_id != user_id and user_id not in referrals_data:
                referrals_data[user_id] = {"referred_by": inviter_id, "rewarded": False}
                if inviter_id in referrals_data:
                    if "count" not in referrals_data[inviter_id]:
                        referrals_data[inviter_id]["count"] = 0
                    referrals_data[inviter_id]["count"] += 1
                else:
                    referrals_data[inviter_id] = {"count": 1}
                save_referrals_data()
        except Exception as e:
            print(f"خطأ في معالجة رابط الإحالة: {e}")

    is_subscribed = await check_user_subscription(user_id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("📢 اشترك في قناة الإثباتات", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ اشتركت، تحقق من الاشتراكات", callback_data="check_sub")]
        ]
        text = "⚠️ **عذراً، يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من استخدام الخدمات.**\n\nقم بالاشتراك ثم اضغط على زر التحقق أدناه 👇"
        if update.message:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if user_id not in user_balances:
        user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
        save_balances()

    if update.message:
        await update.message.reply_text("✨ **مرحباً بك في متجر الخدمات الرقمية**\n\nاختر ما تحتاجه من الأزرار أدناه 👇", reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard()), parse_mode="Markdown")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ هذا الأمر مخصص للمشرفين فقط.")
        return
    
    await update.message.reply_text(
        "🛠 **لوحة تحكم الأدمن:**\n\nاختر العملية المطلوبة من الأزرار أدناه 👇",
        reply_markup=InlineKeyboardMarkup(get_admin_menu_keyboard()),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data == "check_sub":
        is_subscribed = await check_user_subscription(user_id, context)
        if is_subscribed:
            if user_id not in user_balances:
                user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
                save_balances()
            try:
                await query.edit_message_text("✅ تم التحقق بنجاح!\n\nمرحباً بك في متجر الخدمات:", reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard()))
            except:
                pass
        else:
            await query.answer("❌ لم تقم بالاشتراك في القناة بعد!", show_alert=True)
        return

    is_subscribed = await check_user_subscription(user_id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("📢 اشترك في قناة الإثباتات", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ اشتركت، تحقق من الاشتراكات", callback_data="check_sub")]
        ]
        try:
            await query.edit_message_text("⚠️ يجب الاشتراك في القناة أولاً لاستخدام البوت.", reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
        return

    if user_id not in user_balances:
        user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
        save_balances()

    try:
        if data == "search_service_prompt":
            user_states[user_id] = {"step": "waiting_search_query"}
            keyboard = [[InlineKeyboardButton("🔙 إلغاء والرجوع", callback_data="main_menu")]]
            await query.edit_message_text(
                "🔍 **البحث السريع عن الخدمات:**\n\nأرسل الآن كلمة مفتاحية للبحث (مثلاً: `تيك توك`، `لايكات`، `انستقرام`):",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

        elif data == "my_account":
            user_states.pop(user_id, None)
            bal = user_balances.get(user_id, 0.0)
            text = (
                f"👤 **معلومات حسابك:**\n\n"
                f"🆔 الآيدي الخاص بك: `{user_id}`\n"
                f"💰 رصيدك الحالي: `{bal:.2f}` جنيه\n\n"
                f"يمكنك شحن رصيدك عبر فودافون كاش ومراسلة الدعم لتأكيد الشحن."
            )
            keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data == "vodafone_info":
            user_states.pop(user_id, None)
            text = (
                f"💳 **شحن الرصيد عبر فودافون كاش:**\n\n"
                f"قم بتحويل المبلغ المطلوب إلى رقم المحفظة التالي:\n"
                f"📞 رقم المحفظة: `{VODAFONE_WALLET}`\n"
                f"👤 اسم صاحب المحفظة: `{WALLET_NAME}`\n\n"
                f"📸 بعد إتمام التحويل، قم بإرسال **صورة إيصال التحويل** أو **رقم العملية** مباشرة إلى الدعم الفني ليتم إضافة الرصيد لحسابك فوراً 👇"
            )
            keyboard = [
                [InlineKeyboardButton("💬 تواصل مع الدعم لإتمام الشحن", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
            ]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data == "my_favorites":
            user_states.pop(user_id, None)
            favs = user_favorites.get(user_id, [])
            if not favs:
                keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]
                await query.edit_message_text(
                    "⭐ **قائمة خدماتي المفضلة:**\n\nليس لديك أي خدمات مضافة للمفضلة حالياً.",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                return

            keyboard = []
            for s_id in favs:
                found_name = f"خدمة رقم {s_id}"
                for cat in cached_categories:
                    for s in cached_categories[cat]:
                        if str(s.get('service')) == str(s_id):
                            found_name = s.get('name')
                            break
                btn_label = found_name if len(found_name) < 30 else found_name[:30] + "..."
                keyboard.append([InlineKeyboardButton(f"⭐ {btn_label}", callback_data=f"srv_{s_id}")])

            keyboard.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
            await query.edit_message_text("⭐ **خدماتك المفضلة:**\n\nاختر الخدمة للطلب الفوري:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data == "admin_panel":
            if user_id != ADMIN_ID:
                await query.answer("غير مسموح لك!", show_alert=True)
                return
            user_states.pop(user_id, None)
            await query.edit_message_text(
                "🛠 **لوحة تحكم الأدمن:**\n\nاختر العملية المطلوبة 👇",
                reply_markup=InlineKeyboardMarkup(get_admin_menu_keyboard()),
                parse_mode="Markdown"
            )

        elif data == "admin_add_balance":
            if user_id != ADMIN_ID: return
            user_states[user_id] = {"step": "admin_waiting_add"}
            keyboard = [[InlineKeyboardButton("🔙 رجوع لوحة التحكم", callback_data="admin_panel")]]
            await query.edit_message_text(
                "➕ **إضافة رصيد لمستخدم**\n\nأرسل الآن الآيدي ثم المبلغ مفصولين بمسافة:\n`USER_ID AMOUNT`\nمثال: `6738288541 50`",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

        elif data == "admin_sub_balance":
            if user_id != ADMIN_ID: return
            user_states[user_id] = {"step": "admin_waiting_sub"}
            keyboard = [[InlineKeyboardButton("🔙 رجوع لوحة التحكم", callback_data="admin_panel")]]
            await query.edit_message_text(
                "➖ **خصم رصيد من مستخدم**\n\nأرسل الآن الآيدي ثم المبلغ مفصولين بمسافة:\n`USER_ID AMOUNT`\nمثال: `6738288541 20`",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

        elif data == "admin_stats":
            if user_id != ADMIN_ID: return
            site_balance = check_site_balance()
            total_users = len(user_balances)
            keyboard = [[InlineKeyboardButton("🔙 رجوع لوحة التحكم", callback_data="admin_panel")]]
            await query.edit_message_text(
                f"📊 **إحصائيات البوت:**\n\n👥 عدد المستخدمين: `{total_users}`\n💰 رصيد الموقع الحالي: `{site_balance}` دولار",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

        elif data == "show_categories":
            user_states.pop(user_id, None)
            if not cached_categories: 
                load_services()
            
            platforms = ["تيك توك", "فيسبوك", "انستقرام", "سناب شات", "يوتيوب", "تلجرام", "واتساب"]
            keyboard = []
            for p in platforms:
                matched = [c for c in cached_categories if p in c]
                if matched:
                    keyboard.append([InlineKeyboardButton(f"📱 خدمات {p}", callback_data=f"plat_{p}")])
            
            keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")])
            await query.edit_message_text("🔥 **اختر المنصة المطلوبة:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data.startswith("plat_"):
            plat_name = data.replace("plat_", "")
            if not cached_categories:
                load_services()
                
            keyboard = []
            for cat_id, cat_name in category_mapping.items():
                if plat_name in cat_name:
                    btn_text = cat_name if len(cat_name) < 35 else cat_name[:35] + "..."
                    keyboard.append([InlineKeyboardButton(f"📁 {btn_text}", callback_data=f"cat_{cat_id}")])
                    
            keyboard.append([InlineKeyboardButton("🔙 رجوع للمنصات", callback_data="show_categories")])
            await query.edit_message_text(f"📂 **الأقسام المتاحة لخدمات {plat_name}:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data.startswith("cat_"):
            cat_id = data.replace("cat_", "")
            cat_name = category_mapping.get(cat_id, "")
            services_in_cat = cached_categories.get(cat_name, [])
            
            keyboard = []
            for s in services_in_cat[:15]:
                s_id = s.get("service")
                s_name = s.get("name")
                btn_label = s_name if len(s_name) < 30 else s_name[:30] + "..."
                keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"srv_{s_id}")])
                
            keyboard.append([InlineKeyboardButton("🔙 رجوع للمنصات", callback_data="show_categories")])
            await query.edit_message_text(f"📌 **الخدمات في القسم:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data.startswith("srv_"):
            srv_id = data.replace("srv_", "")
            selected_service = None
            for cat in cached_categories:
                for s in cached_categories[cat]:
                    if str(s.get("service")) == str(srv_id):
                        selected_service = s
                        break
                if selected_service:
                    break
                    
            if not selected_service:
                await query.answer("❌ عذراً، هذه الخدمة غير متوفرة حالياً.", show_alert=True)
                return
                
            user_states[user_id] = {"step": "waiting_order_link", "service": selected_service}
            
            text = (
                f"🛒 **تفاصيل الخدمة المختارة:**\n\n"
                f"📌 **اسم الخدمة:** {selected_service.get('name')}\n"
                f"🔢 **رقم الخدمة:** `{selected_service.get('service')}`\n"
                f"💰 **السعر لكل 1000:** `{selected_service.get('client_rate')}` جنيه\n"
                f"📊 **الحد الأدنى:** {selected_service.get('min')}\n"
                f"📈 **الحد الأقصى:** {selected_service.get('max')}\n\n"
                f"🔗 **أرسل الآن الرابط المطلوب لتنفيذ الطلب:**"
            )
            keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data="main_menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data == "free_section":
            user_states.pop(user_id, None)
            if not free_services:
                load_services()
                
            keyboard = []
            for i, s in enumerate(free_services[:10], 1):
                s_name = s['name']
                btn_label = f"🎁 {i}. " + (s_name if len(s_name) < 30 else s_name[:30] + "...")
                keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"srv_{s.get('service')}")])
                
            keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")])
            await query.edit_message_text("🎁 **قسم الرشق اليومي المجاني:**\n\n👇 اختر الخدمة المتاحة للطلب الفوري:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data == "referral_program":
            user_states.pop(user_id, None)
            bot_username = (await context.bot.get_me()).username
            ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
            
            my_invites = 0
            if user_id in referrals_data and "count" in referrals_data[user_id]:
                my_invites = referrals_data[user_id]["count"]

            text = (
                f"👥 **نظام دعوة الأصدقاء:**\n\n"
                f"شارك رابط الدعوة الخاص بك مع أصدقائك، واربح **10%** هدية من قيمة **أول شحنة** يقوم بها كل صديق تدعوه!\n\n"
                f"📊 عدد الأشخاص الذين دعيتهم: `{my_invites}` شخص\n\n"
                f"🔗 **رابط الدعوة الخاص بك:**\n`{ref_link}`\n\n"
                "*(اضغط على الرابط لنسخه وانشره في المجموعات!)*"
            )
            keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

        elif data == "main_menu":
            user_states.pop(user_id, None)
            await query.edit_message_text("✨ **القائمة الرئيسية:**", reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard()), parse_mode="Markdown")

        elif data == "my_orders":
            user_states.pop(user_id, None)
            await update_user_orders_status(user_id, context, update)
            
            user_list_orders = user_orders.get(user_id, [])
            if not user_list_orders:
                keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]]
                await query.edit_message_text(
                    "📦 **سجل طلباتك:**\n\nعذراً، ليس لديك أي طلبات سابقة مسجلة حتى الآن.", 
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                return

            status_translations = {
                "pending": "⏳ قيد الانتظار",
                "in progress": "🔄 قيد التنفيذ",
                "processing": "⚙️ قيد المعالجة",
                "completed": "✅ مكتمل",
                "complete": "✅ مكتمل",
                "success": "✅ مكتمل",
                "partial": "⚠️ جزئي",
                "canceled": "❌ ملغى",
                "cancelled": "❌ ملغى"
            }

            orders_text = "📦 **سجل طلباتك الأخيرة وحالتها:**\n\n"
            
            for o in user_list_orders[-5:]:
                raw_status = str(o.get("status", "pending")).strip().lower()
                formatted_status = status_translations.get(raw_status, f"📌 {o.get('status', 'غير معروف')}")
                
                orders_text += (
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔢 **رقم الطلب:** `{o.get('order_id')}`\n"
                    f"🏷 **الخدمة:** {o.get('service_name', 'خدمة سوشيال ميديا')}\n"
                    f"📊 **الكمية:** {o.get('qty')}\n"
                    f"📌 **الحالة:** {formatted_status}\n"
                )

            keyboard = [
                [InlineKeyboardButton("🔄 تحديث الحالات", callback_data="my_orders")],
                [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
            ]
            
            await query.edit_message_text(
                orders_text, 
                reply_markup=InlineKeyboardMarkup(keyboard), 
                parse_mode="Markdown"
            )
    except Exception as err:
        if "Message is not modified" in str(err):
            pass
        else:
            print(f"خطأ في أزرار التحكم: {err}")

# --- معالجة الرسائل والنصوص المدخلة من المستخدمين ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    
    if user_id not in user_states:
        return
        
    state = user_states[user_id]
    step = state.get("step")
    
    if step == "waiting_search_query":
        user_states.pop(user_id, None)
        if not cached_categories:
            load_services()
            
        found_services = []
        query_lower = text.lower()
        for cat in cached_categories:
            for s in cached_categories[cat]:
                if query_lower in s.get("name", "").lower():
                    found_services.append(s)
                    
        if not found_services:
            keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]
            await update.message.reply_text(f"❌ لم يتم العثور على أي خدمة مطابقة لكلمة: `{text}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            return
            
        keyboard = []
        for s in found_services[:12]:
            s_id = s.get("service")
            s_name = s.get("name")
            btn_label = s_name if len(s_name) < 30 else s_name[:30] + "..."
            keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"srv_{s_id}")])
            
        keyboard.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
        await update.message.reply_text(f"🔍 **نتائج البحث عن ({text}):**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif step == "waiting_order_link":
        selected_service = state.get("service")
        user_states[user_id] = {"step": "waiting_order_qty", "service": selected_service, "link": text}
        
        await update.message.reply_text(
            f"📊 **أدخل الكمية المطلوبة:**\n\n"
            f"الحد الأدنى: `{selected_service.get('min')}`\n"
            f"الحد الأقصى: `{selected_service.get('max')}`",
            parse_mode="Markdown"
        )

    elif step == "waiting_order_qty":
        try:
            qty = int(text)
        except ValueError:
            await update.message.reply_text("❌ يرجى إدخال رقم صحيح للكمية:")
            return
            
        selected_service = state.get("service")
        link = state.get("link")
        
        min_q = int(selected_service.get("min", 1))
        max_q = int(selected_service.get("max", 1000000))
        
        if qty < min_q or qty > max_q:
            await update.message.reply_text(f"❌ الكمية خارج النطاق المسموح به!\nيجب أن تكون بين `{min_q}` و `{max_q}`:", parse_mode="Markdown")
            return
            
        rate = float(selected_service.get("client_rate", 0))
        total_cost = round((qty / 1000.0) * rate, 2)
        
        user_bal = user_balances.get(user_id, 0.0)
        if user_bal < total_cost:
            user_states.pop(user_id, None)
            await update.message.reply_text(
                f"❌ **رصيدك غير كافٍ لإتمام هذا الطلب!**\n\n"
                f"💰 رصيدك الحالي: `{user_bal:.2f}` جنيه\n"
                f"🏷 تكلفة الطلب: `{total_cost:.2f}` جنيه\n\n"
                f"قم بشحن رصيدك عبر فودافون كاش أولاً.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 شحن الرصيد", callback_data="vodafone_info")], [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]),
                parse_mode="Markdown"
            )
            return
            
        try:
            payload = {
                "key": SMM_API_KEY,
                "action": "add",
                "service": selected_service.get("service"),
                "link": link,
                "quantity": qty
            }
            res = requests.post(SMM_API_URL, data=payload, timeout=15).json()
            
            if isinstance(res, dict) and "order" in res:
                order_id = res["order"]
                user_balances[user_id] -= total_cost
                save_balances()
                
                order_info = {
                    "order_id": order_id,
                    "service_name": selected_service.get("name"),
                    "qty": qty,
                    "link": link,
                    "total_cost": total_cost,
                    "status": "Pending"
                }
                
                if user_id not in user_orders:
                    user_orders[user_id] = []
                user_orders[user_id].append(order_info)
                save_orders_data()
                
                user_states.pop(user_id, None)
                await update.message.reply_text(
                    f"✅ **تم إرسال طلبك بنجاح!**\n\n"
                    f"🔢 رقم الطلب: `{order_id}`\n"
                    f"📦 الخدمة: {selected_service.get('name')}\n"
                    f"📊 الكمية: {qty}\n"
                    f"💰 التكلفة المخصومة: `{total_cost:.2f}` جنيه\n"
                    f"💳 رصيدك المتبقي: `{user_balances[user_id]:.2f}` جنيه",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]),
                    parse_mode="Markdown"
                )
            else:
                err_str = res.get("error", "خطأ غير معروف من السيرفر") if isinstance(res, dict) else "استجابة غير صالحة من السيرفر"
                user_states.pop(user_id, None)
                await update.message.reply_text(f"❌ حدث خطأ أثناء إتمام الطلب:\n`{err_str}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]), parse_mode="Markdown")
        except Exception as e:
            user_states.pop(user_id, None)
            await update.message.reply_text(f"❌ خطأ في الاتصال بسيرفر الخدمات: {e}")

    elif step == "admin_waiting_add" and user_id == ADMIN_ID:
        user_states.pop(user_id, None)
        try:
            parts = text.split()
            target_id = int(parts[0])
            amount = float(parts[1])
            
            if target_id not in user_balances:
                user_balances[target_id] = 0.0
            user_balances[target_id] += amount
            save_balances()
            
            await update.message.reply_text(f"✅ تمت إضافة `{amount}` جنيه بنجاح للمستخدم `{target_id}`.", parse_mode="Markdown")
            try:
                await context.bot.send_message(chat_id=target_id, text=f"🎉 **تمت إضافة رصيد لحسابك!**\n\n💰 المبلغ المضاف: `{amount}` جنيه", parse_mode="Markdown")
            except:
                pass
        except Exception as e:
            await update.message.reply_text(f"❌ صيغة غير صحيحة. استخدم: `ID AMOUNT`\nالخطأ: {e}")

    elif step == "admin_waiting_sub" and user_id == ADMIN_ID:
        user_states.pop(user_id, None)
        try:
            parts = text.split()
            target_id = int(parts[0])
            amount = float(parts[1])
            
            if target_id not in user_balances:
                user_balances[target_id] = 0.0
            user_balances[target_id] = max(0.0, user_balances[target_id] - amount)
            save_balances()
            
            await update.message.reply_text(f"✅ تم خصم `{amount}` جنيه بنجاح من المستخدم `{target_id}`.", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ صيغة غير صحيحة. استخدم: `ID AMOUNT`\nالخطأ: {e}")

# --- تشغيل البوت بشكل دائم ---
if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 البوت يعمل الآن بنجاح...")
    load_services()
    application.run_polling()
