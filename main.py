import json
import os
import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "8993779570:AAGWGSOSjbN82X5BsntkkuYsXiJdrDpPWXA"
ADMIN_ID = 8697852304
CHANNEL_ID = -1003931541362
CHANNEL_USERNAME = "Jsoxkedoaoejf"
SUPPORT_USERNAME = "AHMED1_mo600"
SMM_API_URL = "https://igcpanel.com/api/v2"
SMM_API_KEY = "3d5b4555b8c244318fbec23902de49d2"

VODAFONE_WALLET = "01018729516"
WALLET_NAME = "AHMED"
USDT_TRC20_WALLET = "THuftcx4uSZYsjXyhG2kx2W1kGNycxBtbe"

BALANCES_FILE = "user_balances.json"
ORDERS_FILE = "user_orders.json"
REFERRALS_FILE = "user_referrals.json"
FAVS_FILE = "user_favorites.json"
USER_CURRENCIES_FILE = "user_currencies.json"
USER_LANGS_FILE = "user_langs.json"

CURRENCIES = {
    "EGP": {"name": "جنيه مصري 🇪🇬", "rate": 1.0, "symbol": "ج.م"},
    "USD": {"name": "دولار أمريكي 🇺🇸", "rate": 0.021, "symbol": "$"},
    "JOD": {"name": "دينار أردني 🇯🇴", "rate": 0.015, "symbol": "د.أ"},
    "SAR": {"name": "ريال سعودي 🇸🇦", "rate": 0.079, "symbol": "ر.س"},
    "AED": {"name": "درهم إماراتي 🇦🇪", "rate": 0.077, "symbol": "د.إ"},
}

LANGS = {
    "ar": {
        "main_title": "✨ مرحباً بك في متجر الخدمات الرقمية\n\nاختر ما تحتاجه من الأزرار أدناه 👇",
        "btn_services": "🚀 خدمات رشق السوشيال ميديا",
        "btn_search": "🔍 بحث سريع عن خدمة",
        "btn_favs": "⭐ خدماتي المفضلة",
        "btn_orders": "📦 طلباتي السابقة وحالتها",
        "btn_payment": "💳 طرق وشحن الرصيد",
        "btn_account": "👤 حسابي",
        "btn_currency": "💱 تغيير العملة واللغة",
        "btn_support": "💬 تواصل مع الدعم",
        "sub_title": "خدمات رشق السوشيال ميديا",
        "exit": "🚪 خروج",
        "back": "🔙 رجوع",
        "main_menu_btn": "🏠 القائمة الرئيسية",
        "back_step": "⬅️ رجوع خطوة",
        "sub_check": "⚠️ عذراً، يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من استخدام الخدمات.\n\nقم بالاشتراك ثم اضغط على زر التحقق أدناه 👇",
        "sub_btn_channel": "📢 اشترك في قناة الإثباتات",
        "sub_btn_check": "✅ اشتركت، تحقق من الاشتراكات",
        "not_subbed": "❌ لم تقم بالاشتراك في القناة بعد!",
        "currency_title": "🌐 اختر عملة بلدك المفضلة لتحديث أسعار الخدمات أو قم بتغيير لغة البوت:",
        "lang_section": "🌐 تغيير لغة البوت:",
        "lang_ar": "العربية 🇸🇦",
        "lang_en": "English 🇺🇸",
        "choose_lang_done": "✅ تم تغيير اللغة بنجاح إلى العربية."
    },
    "en": {
        "main_title": "✨ Welcome to the Digital Services Store\n\nChoose what you need from the buttons below 👇",
        "btn_services": "🚀 Social Media Services",
        "btn_search": "🔍 Quick Service Search",
        "btn_favs": "⭐ My Favorites",
        "btn_orders": "📦 My Orders & Status",
        "btn_payment": "💳 Balance & Payment Methods",
        "btn_account": "👤 My Account",
        "btn_currency": "💱 Currency & Language",
        "btn_support": "💬 Contact Support",
        "sub_title": "Social Media Services",
        "exit": "🚪 Exit",
        "back": "🔙 Back",
        "main_menu_btn": "🏠 Main Menu",
        "back_step": "⬅️ Back Step",
        "sub_check": "⚠️ Sorry, you must subscribe to the bot channel first to use the services.\n\nSubscribe and then click the check button below 👇",
        "sub_btn_channel": "📢 Subscribe to Channel",
        "sub_btn_check": "✅ I Subscribed, Check",
        "not_subbed": "❌ You haven't subscribed to the channel yet!",
        "currency_title": "🌐 Choose your preferred currency or change bot language:",
        "lang_section": "🌐 Change Bot Language:",
        "lang_ar": "Arabic 🇸🇦",
        "lang_en": "English 🇺🇸",
        "choose_lang_done": "✅ Language successfully changed to English."
    }
}

logging.basicConfig(level=logging.INFO)
cached_subcategories = {} 
free_services = [] 
user_states = {}    

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
user_currencies_data = load_json_file(USER_CURRENCIES_FILE, {})
user_langs_data = load_json_file(USER_LANGS_FILE, {})

def save_balances():
    save_json_file(BALANCES_FILE, user_balances)

def save_orders_data():
    save_json_file(ORDERS_FILE, user_orders)

def save_referrals_data():
    save_json_file(REFERRALS_FILE, referrals_data)

def save_favorites_data():
    save_json_file(FAVS_FILE, user_favorites)

def save_user_currencies():
    save_json_file(USER_CURRENCIES_FILE, user_currencies_data)

def save_user_langs():
    save_json_file(USER_LANGS_FILE, user_langs_data)

def get_user_lang(user_id):
    return user_langs_data.get(str(user_id), "ar")

def get_trans(user_id, key):
    lang = get_user_lang(user_id)
    return LANGS.get(lang, LANGS["ar"]).get(key, LANGS["ar"].get(key, key))

def format_price(user_id, price_in_base):
    curr_code = user_currencies_data.get(str(user_id), "EGP")
    curr_info = CURRENCIES.get(curr_code, CURRENCIES["EGP"])
    converted_price = float(price_in_base) * curr_info["rate"]
    return f"{converted_price:.2f} {curr_info['symbol']}"

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

def detect_service_platform(s_name, cat_name):
    text_s = s_name.lower()
    text_c = cat_name.lower()
    
    digital_tools = ["figma", "canva", "netflix", "shahid", "شاهد", "نتفلكس", "vpn", "adobe", "photoshop", "spotify", "اشتراك سنوي", "اشتراك شهري", "برنامج", "تطبيق مدفوع"]
    if any(tool in text_s or tool in text_c for tool in digital_tools):
        return "أخرى"

    if any(k in text_s for k in ["facebook", "فيسبوك", "فيس", "fb", "meta", "بروفايل فيس", "صفحة فيس"]):
        return "فيسبوك"
    if any(k in text_s for k in ["instagram", "انستقرام", "انستجرام", "انستا", "ig", "قناة انستجرام"]):
        return "انستجرام"
    if any(k in text_s for k in ["tiktok", "تيك توك", "تيكتوك", "تك توك", "tt"]):
        return "تيك توك"
    if any(k in text_s for k in ["whatsapp", "واتساب", "واتس"]):
        return "واتساب"
    if any(k in text_s for k in ["youtube", "يوتيوب", "yt"]):
        return "يوتيوب"
    if any(k in text_s for k in ["telegram", "تليجرام", "تلجرام", "tg"]):
        return "تليجرام"
    if any(k in text_s for k in ["snapchat", "سناب شات", "سناب", "snap"]):
        return "سناب شات"

    if any(k in text_c for k in ["tiktok", "تيك توك"]):
        return "تيك توك"
    if any(k in text_c for k in ["instagram", "انستقرام", "انستجرام", "انستا"]):
        return "انستجرام"
    if any(k in text_c for k in ["facebook", "فيسبوك", "فيس"]):
        return "فيسبوك"
    if any(k in text_c for k in ["whatsapp", "واتساب"]):
        return "واتساب"
    if any(k in text_c for k in ["youtube", "يوتيوب"]):
        return "يوتيوب"
    if any(k in text_c for k in ["telegram", "تليجرام", "تلجرام"]):
        return "تليجرام"
    if any(k in text_c for k in ["snapchat", "سناب شات", "سناب"]):
        return "سناب شات"
        
    return "عام"

def classify_service_type(s_name, cat_name, platform=""):
    text = s_name.lower()
    cat_text = cat_name.lower()
    
    if "===" in text or "---" in text or "___" in text or len(text.strip()) < 3:
        return None

    if any(k in text for k in ["إبلاغ", "ابلاغ", "بلاغ", "reports", "report", "شكوى"]):
        return "الإبلاغات"

    if any(k in text for k in ["استطلاع", "استطلاعات", "تصويت", "تصويتات", "poll", "polls", "vote", "votes"]):
        return "الاستطلاع"

    if any(k in text for k in ["جروب", "مجموعة", "اعضاء جروب", "أعضاء جروب", "group members", "group"]):
        return "أعضاء المجموعات"

    if any(k in text for k in ["comment", "تعليق", "تعليقات", "ردود كتابية", "comments", "كومنت", "كومنتات"]):
        if not any(w in text for w in ["ردود فعل", "تفاعل", "رياكت", "إيموجي", "emoji", "reactions"]):
            return "تعليقات"

    view_keywords = ["view", "views", "مشاهد", "مشاهدات", "reels view", "story view", "live stream views", "livestream views", "snap view"]
    if any(k in text for k in view_keywords) or any(k in cat_text for k in ["view", "views", "مشاهدات"]):
        if not any(w in text for w in ["follower", "متابع", "followers", "متابعين", "like", "لايك", "likes"]):
            return "مشاهدات"

    reaction_keywords = [
        "تعابير", "heart", "love", "reactions", "reaction", "تفاعل", "تفاعلات", 
        "ردود فعل", "إيموجي", "emoji", "رياكت", "رياكتات", "لاف", "ضحك", "واو", 
        "كير", "احضان", "حزين", "غاضب", "رعاك", "دعم"
    ]
    
    if platform == "واتساب":
        if any(k in text for k in reaction_keywords):
            return "التفاعلات"

    follower_keywords = [
        "follower", "متابع", "followers", "متابعين", "subscribers", "مشتركين", 
        "member", "members", "انضمام", "أصدقاء", "أعضاء", "channel members", 
        "group members", "participants", "مشارك", "مشاركون", "snap score", "نقاط سناب"
    ]
    if any(k in text for k in follower_keywords) or any(k in cat_text for k in ["follower", "متابع", "subscriber", "مشترك", "member", "عضو", "أعضاء", "snap"]):
        return "متابعين ومشتركين"

    like_keywords = ["like", "likes", "لايك", "لايكات", "اعجاب", "إعجاب", "أعجبني", "إعجابات"]
    if any(k in text for k in like_keywords):
        if not any(w in text for w in ["متابع", "follower", "followers", "متابعين", "subscribers", "مشتركين"]):
            return "اللايكات"

    if any(k in text for k in reaction_keywords):
        if not any(w in text for w in ["متابع", "follower", "followers", "متابعين"]):
            return "التفاعلات"
    
    return "خدمات أخري"

def load_services():
    global cached_subcategories, free_services
    try:
        response = requests.post(SMM_API_URL, data={"key": SMM_API_KEY, "action": "services"}, timeout=15)
        if response.status_code == 200:
            services_list = response.json()
            
            platforms = ["مجانية", "فيسبوك", "انستجرام", "واتساب", "يوتيوب", "تيك توك", "تليجرام", "سناب شات"]
            temp_sub = {}
            temp_free = []
            
            sub_keys_standard = [
                "متابعين ومشتركين", "اللايكات", "التفاعلات", "الاستطلاع", 
                "مشاهدات", "تعليقات", "الإبلاغات", "أعضاء المجموعات", 
                "خدمات أخري", "خدمات متنوعة"
            ]

            for p in platforms:
                temp_sub[p] = {}
                for sk in sub_keys_standard:
                    temp_sub[p][sk] = []
            
            for s in services_list:
                cat = s.get("category", "")
                s_name = s.get("name", "")
                
                try:
                    original_rate = float(s.get("rate", 0))
                except:
                    original_rate = 0.0

                base_price = original_rate * 50  
                s["api_rate"] = base_price          
                s["client_rate"] = base_price * 1.5   

                if "مجاني" in cat.lower() or "free" in cat.lower() or "مجاني" in s_name.lower() or "free" in s_name.lower() or original_rate == 0:
                    temp_free.append(s)
                    temp_sub["مجانية"]["خدمات متنوعة"].append(s)
                
                real_platform = detect_service_platform(s_name, cat)
                p_type = classify_service_type(s_name, cat, platform=real_platform)
                
                if real_platform in temp_sub and p_type and p_type in temp_sub[real_platform]:
                    temp_sub[real_platform][p_type].append(s)
            
            cleaned_sub = {}
            for p in temp_sub:
                cleaned_sub[p] = {sub_k: items for sub_k, items in temp_sub[p].items() if len(items) > 0}
            
            cached_subcategories = cleaned_sub
            free_services = temp_free
    except Exception as e:
        print(f"خطأ في تحميل الخدمات: {e}")

def get_main_menu_keyboard(user_id=None):
    return [
        [InlineKeyboardButton(get_trans(user_id, "btn_services"), callback_data="show_categories")],
        [InlineKeyboardButton(get_trans(user_id, "btn_search"), callback_data="search_service_prompt")],
        [InlineKeyboardButton(get_trans(user_id, "btn_favs"), callback_data="my_favorites")],
        [InlineKeyboardButton(get_trans(user_id, "btn_orders"), callback_data="my_orders")],
        [InlineKeyboardButton(get_trans(user_id, "btn_payment"), callback_data="payment_methods")],
        [InlineKeyboardButton(get_trans(user_id, "btn_account"), callback_data="my_account")],
        [InlineKeyboardButton(get_trans(user_id, "btn_currency"), callback_data="currency_menu")],
        [InlineKeyboardButton(get_trans(user_id, "btn_support"), url=f"https://t.me/{SUPPORT_USERNAME}")]
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
                        f"💸 **المبلغ:** {format_price(user_id, o.get('total_cost', 0))}\n"
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

async def background_orders_tracker(context: ContextTypes.DEFAULT_TYPE):
    for u_id in list(user_orders.keys()):
        await update_user_orders_status(u_id, context)

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
            [InlineKeyboardButton(get_trans(user_id, "sub_btn_channel"), url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton(get_trans(user_id, "sub_btn_check"), callback_data="check_sub")]
        ]
        text = get_trans(user_id, "sub_check")
        if update.message:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if user_id not in user_balances:
        user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
        save_balances()

    if update.message:
        await update.message.reply_text(get_trans(user_id, "main_title"), reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard(user_id)))

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ هذا الأمر مخصص للمشرفين فقط.")
        return
    
    await update.message.reply_text(
        "🛠 لوحة تحكم الأدمن:\n\nاختر العملية المطلوبة من الأزرار أدناه 👇",
        reply_markup=InlineKeyboardMarkup(get_admin_menu_keyboard())
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data == "exit_action":
        user_states.pop(user_id, None)
        try:
            await query.message.delete()
        except:
            await query.edit_message_text("تم إغلاق القائمة.")
        return

    if data == "currency_menu":
        user_states.pop(user_id, None)
        keyboard = []
        for code, info in CURRENCIES.items():
            keyboard.append([InlineKeyboardButton(info["name"], callback_data=f"set_curr_{code}")])
        
        # إضافة أزرار تغيير اللغة داخل قائمة العملات حسب الطلب
        keyboard.append([
            InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar"),
            InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")
        ])
        keyboard.append([InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")])
        try:
            await query.edit_message_text(get_trans(user_id, "currency_title"), reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
        return

    if data.startswith("set_curr_"):
        chosen_curr = data.replace("set_curr_", "")
        if chosen_curr in CURRENCIES:
            user_currencies_data[str(user_id)] = chosen_curr
            save_user_currencies()
            curr_name = CURRENCIES[chosen_curr]["name"]
            try:
                await query.edit_message_text(f"✅ تم تغيير العملة بنجاح إلى: {curr_name}\n\nتم تحديث الأسعار.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
            except:
                pass
        return

    if data.startswith("set_lang_"):
        chosen_lang = data.replace("set_lang_", "")
        if chosen_lang in ["ar", "en"]:
            user_langs_data[str(user_id)] = chosen_lang
            save_user_langs()
            try:
                await query.edit_message_text(get_trans(user_id, "choose_lang_done"), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
            except:
                pass
        return

    # ميزة إعادة الطلب السريع (Quick Reorder) - تم إضافة الترقيم (1 و 2) بالترتيب فوق بعض
    if data.startswith("reorder_"):
        try:
            target_order_id = data.replace("reorder_", "")
            orders = user_orders.get(user_id, [])
            target_order = None
            for ord_item in orders:
                if str(ord_item.get("order_id")) == str(target_order_id):
                    target_order = ord_item
                    break
            
            if not target_order:
                await query.answer("❌ لم يتم العثور على بيانات هذا الطلب.", show_alert=True)
                return

            s_id = None
            for cat in cached_subcategories:
                for sub_c in cached_subcategories[cat]:
                    for s in cached_subcategories[cat][sub_c]:
                        if str(s.get("name")).strip() == str(target_order.get("service_name")).strip():
                            s_id = s.get("service")
                            break
                    if s_id: break
                if s_id: break

            if not s_id:
                for cat in cached_subcategories:
                    for sub_c in cached_subcategories[cat]:
                        for s in cached_subcategories[cat][sub_c]:
                            if target_order.get("service_name") in s.get("name", ""):
                                s_id = s.get("service")
                                break
                        if s_id: break
                    if s_id: break

            if not s_id:
                await query.answer("❌ عذراً، هذه الخدمة لم تعد متوفرة حالياً في القائمة.", show_alert=True)
                return

            selected_service = None
            for cat in cached_subcategories:
                for sub_c in cached_subcategories[cat]:
                    for s in cached_subcategories[cat][sub_c]:
                        if str(s.get("service")) == str(s_id):
                            selected_service = s
                            break
                    if selected_service: break
                if selected_service: break

            if not selected_service:
                await query.answer("❌ الخدمة غير متوفرة حالياً.", show_alert=True)
                return

            qty = int(target_order.get("qty", 10))
            rate = float(selected_service.get("client_rate", 0))
            total_cost = (qty / 1000) * rate

            if user_balances.get(user_id, 0.0) < total_cost:
                await query.answer("❌ رصيدك الحالي غير كافٍ لإعادة هذا الطلب!", show_alert=True)
                return

            link = target_order.get("link", "")
            payload = {"key": SMM_API_KEY, "action": "add", "service": s_id, "link": link, "quantity": qty}
            res = requests.post(SMM_API_URL, data=payload, timeout=15).json()

            if "order" in res:
                new_order_id = res["order"]
                user_balances[user_id] -= total_cost
                save_balances()

                user_orders[user_id].append({
                    "order_id": new_order_id,
                    "service_name": selected_service.get("name"),
                    "qty": qty,
                    "link": link,
                    "total_cost": round(total_cost, 2),
                    "status": "Pending"
                })
                save_orders_data()

                formatted_rem_bal = format_price(user_id, user_balances[user_id])
                await query.answer("✅ تم إعادة الطلب بنجاح!", show_alert=True)
                try:
                    await query.edit_message_text(
                        f"✅ **تم تقديم طلب الإعادة بنجاح!**\n"
                        f"🔢 رقم الطلب الجديد: {new_order_id}\n"
                        f"📌 الخدمة: {selected_service.get('name')}\n"
                        f"📊 الكمية: {qty}\n"
                        f"🔗 الرابط: {link}\n"
                        f"💰 التكلفة: {format_price(user_id, total_cost)}\n"
                        f"💳 رصيدك المتبقي: {formatted_rem_bal}",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]),
                        parse_mode="Markdown"
                    )
                except:
                    pass
            else:
                await query.answer(f"❌ فشل التنفيذ: {res.get('error', 'خطأ')}", show_alert=True)
        except Exception as e:
            print(f"خطأ في إعادة الطلب السريع: {e}")
            await query.answer("❌ حدث خطأ أثناء محاولة إعادة الطلب.", show_alert=True)
        return

    if data.startswith("approve_dep_") or data.startswith("reject_dep_"):
        if user_id != ADMIN_ID:
            await query.answer("❌ هذا الزر للمشرف فقط!", show_alert=True)
            return
        
        parts = data.split("__")
        action = parts[0]
        target_user_id = int(parts[1])
        amount = float(parts[2].replace("_", "."))
        
        current_caption = query.message.caption or ""
        
        if "approve" in action:
            if target_user_id not in user_balances:
                user_balances[target_user_id] = 0.0
            user_balances[target_user_id] += amount
            save_balances()
            
            new_caption = current_caption + f"\n\n✅ حالة الطلب: تم القبول وإضافة مبلغ ({amount:.2f} جنيه) للمستخدم بنجاح."
            try:
                if query.message.photo:
                    await query.edit_message_caption(caption=new_caption, reply_markup=None)
                else:
                    await query.edit_message_text(text=new_caption, reply_markup=None)
            except:
                pass
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎉 مبروك! تم قبول إيداعك بنجاح.\n\nتمت إضافة مبلغ {amount:.2f} إلى رصيدك."
                )
            except Exception as e:
                print(f"خطأ في إبلاغ المستخدم بالقبول: {e}")
                
        else:
            new_caption = current_caption + "\n\n❌ حالة الطلب: تم رفض عملية الإيداع."
            try:
                if query.message.photo:
                    await query.edit_message_caption(caption=new_caption, reply_markup=None)
                else:
                    await query.edit_message_text(text=new_caption, reply_markup=None)
            except:
                pass
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="❌ عذراً، تم رفض عملية الإيداع الخاصة بك من قبل الإدارة.\n\nإذا كانت هناك مشكلة، يرجى التواصل مع الدعم."
                )
            except Exception as e:
                print(f"خطأ في إبلاغ المستخدم بالرفض: {e}")
        return

    if data == "check_sub":
        is_subscribed = await check_user_subscription(user_id, context)
        if is_subscribed:
            if user_id not in user_balances:
                user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
                save_balances()
            try:
                await query.edit_message_text("✅ تم التحقق بنجاح!\n\nمرحباً بك في متجر الخدمات:", reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard(user_id)))
            except:
                pass
        else:
            await query.answer(get_trans(user_id, "not_subbed"), show_alert=True)
        return

    is_subscribed = await check_user_subscription(user_id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton(get_trans(user_id, "sub_btn_channel"), url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton(get_trans(user_id, "sub_btn_check"), callback_data="check_sub")]
        ]
        try:
            await query.edit_message_text(get_trans(user_id, "sub_check"), reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
        return

    if user_id not in user_balances:
        user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
        save_balances()

    try:
        if data == "search_service_prompt":
            user_states[user_id] = {"step": "waiting_search_query"}
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ]
            await query.edit_message_text(
                "🔍 البحث السريع عن الخدمات:\n\nأرسل الآن كلمة مفتاحية للبحث:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data == "my_account":
            user_states.pop(user_id, None)
            bal = user_balances.get(user_id, 0.0)
            formatted_bal = format_price(user_id, bal)
            text = (
                f"👤 معلومات حسابك:\n\n"
                f"🆔 الآيدي الخاص بك: {user_id}\n"
                f"💰 رصيدك الحالي: {formatted_bal}\n"
            )
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "payment_methods":
            user_states.pop(user_id, None)
            text = "💳 اختر طريقة الشحن المناسبة لك:"
            keyboard = [
                [InlineKeyboardButton("📞 شحن عبر فودافون كاش", callback_data="pay_vodafone")],
                [InlineKeyboardButton("🪙 شحن عبر USDT (TRC-20)", callback_data="pay_usdt")],
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "pay_vodafone":
            user_states[user_id] = {"step": "deposit_waiting_screenshot", "method": "فودافون كاش"}
            text = f"📞 تحويل على رقم: {VODAFONE_WALLET}\nاسم الحساب: {WALLET_NAME}\n\n📸 أرسل صورة الإيصال (اسكرين شوت):"
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="payment_methods")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="payment_methods")]
            ]
            try:
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "pay_usdt":
            user_states[user_id] = {"step": "deposit_waiting_screenshot", "method": "USDT (TRC20)"}
            text = f"🪙 عنوان المحفظة:\n{USDT_TRC20_WALLET}\n\n📸 أرسل صورة الإيصال (اسكرين شوت):"
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="payment_methods")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="payment_methods")]
            ]
            try:
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "my_favorites":
            user_states.pop(user_id, None)
            favs = user_favorites.get(user_id, [])
            if not favs:
                keyboard = [
                    [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                    [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
                ]
                try:
                    await query.edit_message_text("⭐ ليس لديك أي خدمات في المفضلة.", reply_markup=InlineKeyboardMarkup(keyboard))
                except:
                    pass
                return

            keyboard = []
            for s_id in favs:
                found_name = f"خدمة رقم {s_id}"
                for cat in cached_subcategories:
                    for sub_c in cached_subcategories[cat]:
                        for s in cached_subcategories[cat][sub_c]:
                            if str(s.get('service')) == str(s_id):
                                raw_name = s.get('name')
                                if len(raw_name) > 40:
                                    found_name = f"🔸 {raw_name[:37]}..."
                                else:
                                    found_name = f"🔸 {raw_name}"
                                break
                keyboard.append([InlineKeyboardButton(found_name, callback_data=f"srv_{s_id}")])

            keyboard.extend([
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ])
            try:
                await query.edit_message_text("⭐ خدماتك المفضلة:", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "my_orders":
            user_states.pop(user_id, None)
            await update_user_orders_status(user_id, context, update_obj=update)
            
            orders = user_orders.get(user_id, [])
            if not orders:
                keyboard = [
                    [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                    [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
                ]
                try:
                    await query.edit_message_text("📦 ليس لديك أي طلبات سابقة.", reply_markup=InlineKeyboardMarkup(keyboard))
                except:
                    pass
                return

            text_orders = "📦 طلباتك السابقة:\n\n"
            keyboard = []

            for idx, order in enumerate(orders[-10:], 1):
                o_id = order.get('order_id')
                status_str = order.get('status', 'قيد التنفيذ 🔄')
                if status_str.lower() in ["completed", "complete", "success"]:
                    status_str = "تم التسليم ✅"

                formatted_cost = format_price(user_id, order.get('total_cost', 0))
                text_orders += (
                    f"--- الطلب #{idx} ---\n"
                    f"📌 الخدمة: {order.get('service_name', 'غير معروف')}\n"
                    f"🆔 رقم الطلب: {o_id}\n"
                    f"📊 الكمية: {order.get('qty', '-')}\n"
                    f"💰 التكلفة: {formatted_cost}\n"
                    f"📌 الحالة: {status_str}\n\n"
                )
                keyboard.append([InlineKeyboardButton(f"{idx} 🔄 إعادة طلب رقم {o_id}", callback_data=f"reorder_{o_id}")])

            keyboard.extend([
                [InlineKeyboardButton("🔄 تحديث حالة الطلبات", callback_data="my_orders")],
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ])
            try:
                await query.edit_message_text(text_orders, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "admin_panel":
            if user_id != ADMIN_ID: return
            user_states.pop(user_id, None)
            try:
                await query.edit_message_text("🛠 لوحة تحكم الأدمن:", reply_markup=InlineKeyboardMarkup(get_admin_menu_keyboard()))
            except:
                pass

        elif data == "admin_add_balance":
            if user_id != ADMIN_ID: return
            user_states[user_id] = {"step": "admin_waiting_add"}
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
            try:
                await query.edit_message_text("➕ أرسل: USER_ID AMOUNT", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "admin_sub_balance":
            if user_id != ADMIN_ID: return
            user_states[user_id] = {"step": "admin_waiting_sub"}
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
            try:
                await query.edit_message_text("➖ أرسل: USER_ID AMOUNT", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "admin_stats":
            if user_id != ADMIN_ID: return
            site_balance = check_site_balance()
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
            try:
                await query.edit_message_text(f"📊 رصيد الموقع: {site_balance} دولار", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "show_categories":
            user_states.pop(user_id, None)
            if not cached_subcategories: 
                load_services()
            
            keyboard = [
                [InlineKeyboardButton("خدمات مجانيه 🎁", callback_data="platform_مجانية")],
                [InlineKeyboardButton("خدمات فيسبوك 📘", callback_data="platform_فيسبوك")],
                [InlineKeyboardButton("خدمات انستجرام 📸", callback_data="platform_انستجرام")],
                [InlineKeyboardButton("خدمات واتساب 🟢", callback_data="platform_واتساب")],
                [InlineKeyboardButton("خدمات يوتيوب 🟥", callback_data="platform_يوتيوب")],
                [InlineKeyboardButton("خدمات تيك توك 🎬", callback_data="platform_تيك توك")],
                [InlineKeyboardButton("خدمات تليجرام ✈️", callback_data="platform_تليجرام")],
                [InlineKeyboardButton("خدمات سناب شات 👻", callback_data="platform_سناب شات")],
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text(get_trans(user_id, "sub_title"), reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data.startswith("platform_"):
            platform_name = data.replace("platform_", "")
            sub_dict = cached_subcategories.get(platform_name, {})
            
            keyboard = []
            for sub_cat_name in sub_dict:
                count_s = len(sub_dict[sub_cat_name])
                if count_s > 0:
                    keyboard.append([InlineKeyboardButton(f"📂 {sub_cat_name} ({count_s})", callback_data=f"subcat_{platform_name}__{sub_cat_name}__0")])
            
            keyboard.extend([
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="show_categories")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="show_categories")]
            ])
            try:
                await query.edit_message_text(f"أقسام خدمات {platform_name}:", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data.startswith("subcat_"):
            parts = data.split("__")
            platform_name = parts[0].replace("subcat_", "")
            sub_cat_name = parts[1]
            page = int(parts[2])
            
            services_in_sub = cached_subcategories.get(platform_name, {}).get(sub_cat_name, [])
            items_per_page = 10
            total_items = len(services_in_sub)
            max_pages = (total_items - 1) // items_per_page if total_items > 0 else 0
            
            start_idx = page * items_per_page
            end_idx = start_idx + items_per_page
            current_services = services_in_sub[start_idx:end_idx]
            
            keyboard = []
            for s in current_services:
                s_id = s.get("service")
                s_name = s.get("name", "")
                
                if len(s_name) > 42:
                    btn_text = f"🔸 {s_name[:39]}..."
                else:
                    btn_text = f"🔸 {s_name}"
                
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"srv_{s_id}")])
                
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"subcat_{platform_name}__{sub_cat_name}__{page - 1}"))
            if page < max_pages:
                nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"subcat_{platform_name}__{sub_cat_name}__{page + 1}"))
            
            if nav_buttons:
                keyboard.append(nav_buttons)
                
            keyboard.extend([
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data=f"platform_{platform_name}")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data=f"platform_{platform_name}")]
            ])
            
            text_msg = f"خدمات {platform_name} 🏷 ({sub_cat_name})\nصفحة {page + 1} من {max_pages + 1}" if services_in_sub else f"❌ لا توجد خدمات في هذا القسم."
            try:
                await query.edit_message_text(text_msg, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data.startswith("srv_"):
            s_id = data.replace("srv_", "")
            selected_service = None
            back_target = "show_categories"
            
            for cat in cached_subcategories:
                for sub_c in cached_subcategories[cat]:
                    for s in cached_subcategories[cat][sub_c]:
                        if str(s.get("service")) == str(s_id):
                            selected_service = s
                            back_target = f"subcat_{cat}__{sub_c}__0"
                            break
                    if selected_service: break
                if selected_service: break
            
            if not selected_service:
                await query.answer("❌ الخدمة غير متوفرة.", show_alert=True)
                return

            user_states[user_id] = {"step": "waiting_quantity", "service_id": s_id, "cat_back": back_target}
            
            s_name = selected_service.get("name")
            rate = selected_service.get("client_rate", 0)
            formatted_rate = format_price(user_id, rate)
            min_q = selected_service.get("min", 10)
            max_q = selected_service.get("max", 10000)
            
            text = (
                f"🛒 تفاصيل الخدمة:\n\n"
                f"📌 الاسم: {s_name}\n"
                f"🆔 رقم الخدمة: {s_id}\n"
                f"💰 السعر لكل 1000: {formatted_rate}\n"
                f"📉 الحد الأدنى: {min_q}\n"
                f"📈 الحد الأقصى: {max_q}\n\n"
                f"📊 أرسل الآن الكمية المطلوبة:"
            )
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data=back_target)],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data=back_target)]
            ]
            try:
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

        elif data == "main_menu":
            user_states.pop(user_id, None)
            try:
                await query.edit_message_text(
                    get_trans(user_id, "main_title"), 
                    reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard(user_id))
                )
            except:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=get_trans(user_id, "main_title"),
                    reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard(user_id))
                )

    except Exception as e:
        print(f"خطأ في button_handler: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in user_states and user_states[user_id].get("step") == "deposit_waiting_screenshot":
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            user_states[user_id]["screenshot"] = photo_file_id
            user_states[user_id]["step"] = "deposit_waiting_phone"
            await update.message.reply_text("📱 الخطوة 2: أرسل رقم الهاتف المرسل منه:")
            return
        else:
            await update.message.reply_text("❌ يرجى إرسال صورة الإيصال كصورة صحيحة:")
            return

    if not update.message.text:
        return
        
    text = update.message.text.strip()
    
    if user_id in user_states:
        state_data = user_states[user_id]
        step = state_data.get("step")
        
        if step == "deposit_waiting_phone":
            user_states[user_id]["phone"] = text
            user_states[user_id]["step"] = "deposit_waiting_amount"
            await update.message.reply_text("💰 الخطوة 3: أرسل المبلغ الذي تم تحويله:")
            return

        elif step == "deposit_waiting_amount":
            amount_text = text.replace(",", ".")
            method = state_data.get("method")
            screenshot = state_data.get("screenshot")
            phone = state_data.get("phone")
            user_states.pop(user_id, None)
            
            try:
                numeric_amount = float(amount_text)
            except:
                numeric_amount = 0.0

            admin_msg = (
                f"📥 طلب شحن رصيد جديد!\n\n"
                f"👤 المستخدم: {user_id}\n"
                f"💳 الطريقة: {method}\n"
                f"📱 رقم المرسل: {phone}\n"
                f"💵 المبلغ: {numeric_amount}\n"
            )
            
            amount_str_safe = str(numeric_amount).replace(".", "_")
            admin_keyboard = [[
                InlineKeyboardButton("✅ قبول", callback_data=f"approve_dep__{user_id}__{amount_str_safe}"),
                InlineKeyboardButton("❌ رفض", callback_data=f"reject_dep__{user_id}__{amount_str_safe}")
            ]]
            
            try:
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=screenshot, caption=admin_msg, reply_markup=InlineKeyboardMarkup(admin_keyboard))
            except:
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, reply_markup=InlineKeyboardMarkup(admin_keyboard))

            await update.message.reply_text("✅ تم إرسال طلب الشحن بنجاح للإدارة.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
            return

        elif step == "waiting_search_query":
            user_states.pop(user_id, None)
            query_str = text.lower()
            matching_services = []
            
            for cat in cached_subcategories:
                for sub_c in cached_subcategories[cat]:
                    for s in cached_subcategories[cat][sub_c]:
                        if query_str in s.get("name", "").lower():
                            matching_services.append(s)
            
            if not matching_services:
                await update.message.reply_text("❌ لم يتم العثور على خدمات.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                return
            
            keyboard = []
            for s in matching_services[:15]:
                s_id = s.get("service")
                s_name = s.get("name", "")
                if len(s_name) > 42:
                    btn_text = f"🔍 {s_name[:39]}..."
                else:
                    btn_text = f"🔍 {s_name}"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"srv_{s_id}")])
                
            keyboard.append([InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")])
            await update.message.reply_text(f"🔍 نتائج البحث:", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        elif step == "waiting_quantity":
            try:
                qty = int(text)
            except ValueError:
                await update.message.reply_text("❌ يرجى إدخال رقم صحيح للكمية:")
                return
            
            s_id = state_data.get("service_id")
            cat_back = state_data.get("cat_back", "show_categories")
            
            selected_service = None
            for cat in cached_subcategories:
                for sub_c in cached_subcategories[cat]:
                    for s in cached_subcategories[cat][sub_c]:
                        if str(s.get("service")) == str(s_id):
                            selected_service = s
                            break
                    if selected_service: break
                if selected_service: break
            
            if not selected_service:
                await update.message.reply_text("❌ حدث خطأ، يرجى المحاولة لاحقاً.")
                return
                
            min_q = int(selected_service.get("min", 10))
            max_q = int(selected_service.get("max", 10000))
            
            if qty < min_q or qty > max_q:
                await update.message.reply_text(f"❌ الكمية يجب أن بين {min_q} و {max_q}.")
                return
                
            rate = float(selected_service.get("client_rate", 0))
            total_cost = (qty / 1000) * rate
            
            if user_balances.get(user_id, 0.0) < total_cost:
                await update.message.reply_text("❌ رصيدك الحالي غير كافٍ لهذا الطلب.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 شحن الرصيد", callback_data="payment_methods")]]))
                return

            user_states[user_id] = {"step": "waiting_link", "service_id": s_id, "qty": qty, "total_cost": total_cost, "cat_back": cat_back}
            formatted_cost = format_price(user_id, total_cost)
            await update.message.reply_text(f"🔗 التكلفة الإجمالية: {formatted_cost}\n\nأرسل الآن الرابط المطلوب لتنفيذ الخدمة:")
            return

        elif step == "waiting_link":
            link = text
            s_id = state_data.get("service_id")
            qty = state_data.get("qty")
            total_cost = state_data.get("total_cost")
            user_states.pop(user_id, None)
            
            selected_service = None
            for cat in cached_subcategories:
                for sub_c in cached_subcategories[cat]:
                    for s in cached_subcategories[cat][sub_c]:
                        if str(s.get("service")) == str(s_id):
                            selected_service = s
                            break
                    if selected_service: break
                if selected_service: break
            
            if not selected_service:
                await update.message.reply_text("❌ حدث خطأ، يرجى المحاولة لاحقاً.")
                return

            if user_balances.get(user_id, 0.0) < total_cost:
                await update.message.reply_text("❌ رصيدك الحالي غير كافٍ.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 شحن الرصيد", callback_data="payment_methods")]]))
                return
            
            payload = {"key": SMM_API_KEY, "action": "add", "service": s_id, "link": link, "quantity": qty}
            try:
                res = requests.post(SMM_API_URL, data=payload, timeout=15).json()
                if "order" in res:
                    order_id = res["order"]
                    user_balances[user_id] -= total_cost
                    save_balances()
                    
                    if user_id not in user_orders: user_orders[user_id] = []
                    user_orders[user_id].append({
                        "order_id": order_id, 
                        "service_name": selected_service.get("name"), 
                        "qty": qty, 
                        "link": link,
                        "total_cost": round(total_cost, 2),
                        "status": "Pending"
                    })
                    save_orders_data()
                    
                    formatted_rem_bal = format_price(user_id, user_balances[user_id])
                    await update.message.reply_text(f"✅ تم تقديم طلبك بنجاح!\nرقم الطلب: {order_id}\nرصيدك المتبقي: {formatted_rem_bal}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                else:
                    await update.message.reply_text(f"❌ فشل التنفيذ: {res.get('error', 'خطأ')}")
            except:
                await update.message.reply_text("❌ خطأ في الاتصال بالسيرفر.")
            return

        elif step in ["admin_waiting_add", "admin_waiting_sub"]:
            if user_id != ADMIN_ID: return
            user_states.pop(user_id, None)
            parts = text.split()
            try:
                target_id = int(parts[0])
                amount = float(parts[1])
            except Exception:
                await update.message.reply_text("❌ الصيغة خاطئة. استخدم: USER_ID AMOUNT")
                return
            
            if target_id not in user_balances: user_balances[target_id] = 0.0
            if step == "admin_waiting_add":
                user_balances[target_id] += amount
            else:
                user_balances[target_id] = max(0.0, user_balances[target_id] - amount)
            save_balances()
            await update.message.reply_text(f"✅ تم التعديل بنجاح للمستخدم {target_id}. الرصيد الحالي: {user_balances[target_id]}")
            return

def main():
    load_services()
    app = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build() # type: ignore
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(background_orders_tracker, interval=30, first=5)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("damin", admin_command))
    app.add_handler(CommandHandler("panel", admin_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle_message))
    
    print("البوت يعمل الآن مع ميزة تغيير اللغة داخل زر العملات ودون المساس بالباقي...")
    app.run_polling()

if __name__ == "__main__":
    main()