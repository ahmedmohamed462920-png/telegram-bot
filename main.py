import json
import os
import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "8942289190:AAFaylYUr3ySiUUCntptfXdTz8TcFCM7JRs"
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
    query = update.