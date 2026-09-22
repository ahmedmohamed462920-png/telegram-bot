import json
import os
import logging
import time
import random
import requests
import asyncio
from pymongo import MongoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN =8693513468:AAFMHTAya-ahSeqsqaXU9qnJE6E8NdmEQPE"
ADMIN_ID = 8661031937
CHANNEL_ID = -1004333526788
CHANNEL_USERNAME = "Jsoxkedoaoejfh"
SUPPORT_USERNAME = "Hdiwjfk65BT"
SMM_API_URL = "https://smmxsocial.com/api/v2"
SMM_API_KEY = "bb0e2136a9676606079a027aeb10ea5c"

MONGO_URI = "mongodb://ahmed462920mohamed_db_user:9YNC0fcUy02liEdV@ac-h69by4r-shard-00-00.ksgqrjd.mongodb.net:27017,ac-h69by4r-shard-00-01.ksgqrjd.mongodb.net:27017,ac-h69by4r-shard-00-02.ksgqrjd.mongodb.net:27017/?ssl=true&replicaSet=atlas-adx6rj-shard-0&authSource=admin&appName=Cluster0"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_smm_bot"]

balances_col = db["user_balances"]
orders_col = db["user_orders"]
referrals_col = db["user_referrals"]
favorites_col = db["user_favorites"]
currencies_col = db["user_currencies"]
langs_col = db["user_langs"]
banned_col = db["user_banned"]
settings_col = db["bot_settings"]
promo_codes_col = db["promo_codes"]
daily_gifts_col = db["daily_gifts_claims"]

VODAFONE_WALLET = "01004842492"
WALLET_NAME = "MAHMOUD"
USDT_TRC20_WALLET = "THuftcx4uSZYsjXyhG2kx2W1kGNycxBtbe"

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
        "btn_promo": "🎟 شحن كود هدية",
        "btn_daily_gift": "🎁 الهدية اليومية المجانية",
        "btn_account": "👤 حسابي",
        "btn_currency": "💱 تغيير العملة واللغة",
        "btn_support": "💬 تواصل مع الدعم",
        "sub_title": "خدمات رشق السوشيال ميديا",
        "exit": "🚪 خروج",
        "back": "🔙 رجوع",
        "main_menu_btn": "🏠 القائمة الرئيسية",
        "back_step": "⬅️ رجوع خطوة",
        "sub_check": "⚠️ عذراً، يجب عليك الاشتراك في قناة البوت أولاًلتتمكن من استخدام الخدمات.\n\nقم بالاشتراك ثم اضغط على زر التحقق أدناه 👇",
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
        "btn_promo": "🎟 Redeem Promo Code",
        "btn_daily_gift": "🎁 Free Daily Gift",
        "btn_account": "👤 My Account",
        "btn_currency": "💱 Currency & Language",
        "btn_support": "💬 Contact Support",
        "sub_title": "Social Media Services",
        "exit": "🚪 Exit",
        "back": "🔙 Back",
        "main_menu_btn": "Main Menu",
        "back_step": "Back Step",
        "sub_check": "⚠️ Sorry, you must subscribe to the bot channel first to use the services.\n\nSubscribe and then click the check button below 👇",
        "sub_btn_channel": "📢 Subscribe to Channel",
        "sub_btn_check": "✅ I Subscribed, Check",
        "not_subbed": "❌ You haven't subscribed to the channel yet!",
        "currency_title": "🌐 Choose your preferred currency or change bot language:",
        "lang_section": "🌐 Change Bot Language:",
        "lang_ar": "Arabic 🇸🇦",
        "lang_en": "English 🇺🇸",
        "choose_lang_done": "🎁 Language successfully changed to English."
    }
}

logging.basicConfig(level=logging.INFO)
cached_subcategories = {} 
subcat_keys_map = {} 
daily_gift_cache = {"services": [], "day": ""}
user_states = {}    

def load_settings():
    doc = settings_col.find_one({"_id": "global_settings"})
    if doc:
        return float(doc.get("profit_margin", 1.35))
    return 1.35

def save_settings(margin):
    settings_col.update_one({"_id": "global_settings"}, {"$set": {"profit_margin": float(margin)}}, upsert=True)

PROFIT_MARGIN = load_settings()

def load_balances_db():
    data = {}
    for doc in balances_col.find():
        data[int(doc["user_id"])] = float(doc["balance"])
    return data

def save_balances_db(data):
    for uid, bal in data.items():
        balances_col.update_one({"user_id": int(uid)}, {"$set": {"balance": float(bal)}}, upsert=True)

def load_orders_db():
    data = {}
    for doc in orders_col.find():
        data[int(doc["user_id"])] = doc["orders"]
    return data

def save_orders_db(data):
    for uid, ords in data.items():
        orders_col.update_one({"user_id": int(uid)}, {"$set": {"orders": ords}}, upsert=True)

def load_referrals_db():
    data = {}
    for doc in referrals_col.find():
        data[int(doc["user_id"])] = doc["data"]
    return data

def save_referrals_db(data):
    for uid, ref_data in data.items():
        referrals_col.update_one({"user_id": int(uid)}, {"$set": {"data": ref_data}}, upsert=True)

def load_favorites_db():
    data = {}
    for doc in favorites_col.find():
        data[int(doc["user_id"])] = doc["favorites"]
    return data

def save_favorites_db(data):
    for uid, favs in data.items():
        favorites_col.update_one({"user_id": int(uid)}, {"$set": {"favorites": favs}}, upsert=True)

def load_currencies_db():
    data = {}
    for doc in currencies_col.find():
        data[str(doc["user_id"])] = doc["currency"]
    return data

def save_currencies_db(data):
    for uid, curr in data.items():
        currencies_col.update_one({"user_id": str(uid)}, {"$set": {"currency": curr}}, upsert=True)

def load_langs_db():
    data = {}
    for doc in langs_col.find():
        data[str(doc["user_id"])] = doc["lang"]
    return data

def save_langs_db(data):
    for uid, lang in data.items():
        langs_col.update_one({"user_id": str(uid)}, {"$set": {"lang": lang}}, upsert=True)

def load_banned_db():
    banned = set()
    for doc in banned_col.find():
        banned.add(int(doc["user_id"]))
    return banned

def save_banned_db(uid, is_banned):
    if is_banned:
        banned_col.update_one({"user_id": int(uid)}, {"$set": {"banned": True}}, upsert=True)
    else:
        banned_col.delete_one({"user_id": int(uid)})

user_balances = load_balances_db()
user_orders = load_orders_db()
referrals_data = load_referrals_db()
user_favorites = load_favorites_db()
user_currencies_data = load_currencies_db()
user_langs_data = load_langs_db()
banned_users = load_banned_db()

def save_balances():
    save_balances_db(user_balances)

def save_orders_data():
    save_orders_db(user_orders)

def save_referrals_data():
    save_referrals_db(referrals_data)

def save_favorites_data():
    save_favorites_db(user_favorites)

def save_user_currencies():
    save_currencies_db(user_currencies_data)

def save_user_langs():
    save_langs_db(user_langs_data)

def get_user_lang(user_id):
    return user_langs_data.get(str(user_id), "ar")

def get_trans(user_id, key):
    lang = get_user_lang(user_id)
    return LANGS.get(lang, LANGS["ar"]).get(key, LANGS["ar"].get(key, key))

def translate_status(status_str):
    s = str(status_str).strip().lower()
    if s in ["completed", "complete", "success", "finished", "done"]:
        return "تم التسليم ✅"
    elif s in ["in progress", "inprogress", "processing", "pending"]:
        return "قيد التنفيذ 🔄"
    elif s in ["canceled", "cancelled"]:
        return "ملغي ❌"
    elif s in ["partial"]:
        return "مكتمل جزئياً ⚠️"
    return status_str

def format_price(user_id, price_in_base):
    curr_code = user_currencies_data.get(str(user_id), "EGP")
    curr_info = CURRENCIES.get(curr_code, CURRENCIES["EGP"])
    converted_price = float(price_in_base) * curr_info["rate"]
    
    if 0 < converted_price < 0.01:
        return f"{converted_price:.4f} {curr_info['symbol']}"
    return f"{converted_price:.2f} {curr_info['symbol']}"

def detect_service_platform(s_name, cat_name):
    text_s = s_name.lower()
    text_c = cat_name.lower()
    
    digital_tools = ["figma", "canva", "netflix", "shahid", "شاهد", "نتفلكس", "vpn", "adobe", "photoshop", "spotify", "اشتراك سنوي", "اشتراك شهري", "برنامج", "تطبيق مدفوع"]
    if any(tool in text_s or tool in text_c for tool in digital_tools):
        return "أخرى"

    if any(k in text_s for k in ["facebook", "فيسبوك", "فيس", "fb", "meta"]):
        return "فيسبوك"
    if any(k in text_s for k in ["instagram", "انستقرام", "انستجرام", "انستا", "ig"]):
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
        "ردود فعل", "إيموجي", "emoji", "رياكت", "رياكتات", "لاف", "ضحك", "واو"
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

async def load_services():
    global cached_subcategories, daily_gift_cache, subcat_keys_map
    try:
        def fetch_smm():
            return requests.post(SMM_API_URL, data={"key": SMM_API_KEY, "action": "services"}, timeout=15)
        
        response = await asyncio.to_thread(fetch_smm)
        if response.status_code == 200:
            services_list = response.json()
            
            platforms = ["فيسبوك", "انستجرام", "واتساب", "يوتيوب", "تيك توك", "تليجرام", "سناب شات"]
            temp_sub = {}
            for p in platforms:
                temp_sub[p] = {}
                for sk in ["متابعين ومشتركين", "اللايكات", "التفاعلات", "الاستطلاع", "مشاهدات", "تعليقات", "الإبلاغات", "أعضاء المجموعات", "خدمات أخري"]:
                    temp_sub[p][sk] = []
            
            all_valid_services = []
            for s in services_list:
                cat = s.get("category", "")
                s_name = s.get("name", "")
                
                try:
                    original_rate = float(s.get("rate", 0))
                except:
                    original_rate = 0.0

                base_price = original_rate * 50  
                s["api_rate"] = base_price          
                s["client_rate"] = base_price * PROFIT_MARGIN  

                real_platform = detect_service_platform(s_name, cat)
                if real_platform == "أخرى" or real_platform == "عام":
                    continue

                p_type = classify_service_type(s_name, cat, platform=real_platform)
                if real_platform in temp_sub and p_type:
                    temp_sub[real_platform][p_type].append(s)

                all_valid_services.append(s)
            
            cleaned_sub = {}
            subcat_keys_map.clear()
            idx_counter = 1
            for p in temp_sub:
                cleaned_sub[p] = {}
                for sub_k, items in temp_sub[p].items():
                    if len(items) > 0:
                        cleaned_sub[p][sub_k] = items
                        subcat_keys_map[str(idx_counter)] = (p, sub_k)
                        subcat_keys_map[f"{p}__{sub_k}"] = str(idx_counter)
                        idx_counter += 1

            cached_subcategories = cleaned_sub

            if all_valid_services:
                current_date_str = time.strftime("%Y-%m-%d")
                if daily_gift_cache["day"] != current_date_str or not daily_gift_cache["services"]:
                    services_by_platform = {}
                    for s_item in all_valid_services:
                        cat = s_item.get("category", "")
                        s_name = s_item.get("name", "")
                        plt = detect_service_platform(s_name, cat)
                        if plt not in services_by_platform:
                            services_by_platform[plt] = []
                        services_by_platform[plt].append(s_item)

                    available_platforms = [plt for plt, s_list in services_by_platform.items() if len(s_list) > 0]
                    chosen_two = []
                    
                    if len(available_platforms) >= 2:
                        sampled_platforms = random.sample(available_platforms, 2)
                        for plt in sampled_platforms:
                            chosen_two.append(random.choice(services_by_platform[plt]))
                    elif len(available_platforms) == 1:
                        s_list = services_by_platform[available_platforms[0]]
                        if len(s_list) >= 2:
                            chosen_two = random.sample(s_list, 2)
                        elif len(s_list) == 1:
                            chosen_two = [s_list[0], s_list[0]]
                    else:
                        if len(all_valid_services) >= 2:
                            chosen_two = random.sample(all_valid_services, 2)
                        elif len(all_valid_services) == 1:
                            chosen_two = [all_valid_services[0], all_valid_services[0]]
                        else:
                            chosen_two = []
                    
                    gift_services_list = []
                    for s_item in chosen_two:
                        srv_copy = s_item.copy()
                        srv_copy["min"] = 10
                        srv_copy["max"] = 10
                        srv_copy["client_rate"] = 0.0  
                        gift_services_list.append(srv_copy)

                    daily_gift_cache["services"] = gift_services_list
                    daily_gift_cache["day"] = current_date_str

    except Exception as e:
        print(f"خطأ في تحميل الخدمات: {e}")

def get_main_menu_keyboard(user_id=None):
    return [
        [InlineKeyboardButton(get_trans(user_id, "btn_services"), callback_data="show_categories")],
        [InlineKeyboardButton(get_trans(user_id, "btn_daily_gift"), callback_data="daily_gift_menu")], 
        [InlineKeyboardButton(get_trans(user_id, "btn_search"), callback_data="search_service_prompt")],
        [InlineKeyboardButton(get_trans(user_id, "btn_favs"), callback_data="my_favorites")],
        [InlineKeyboardButton(get_trans(user_id, "btn_orders"), callback_data="my_orders")],
        [InlineKeyboardButton(get_trans(user_id, "btn_payment"), callback_data="payment_methods")],
        [InlineKeyboardButton(get_trans(user_id, "btn_promo"), callback_data="promo_code_prompt")],
        [InlineKeyboardButton(get_trans(user_id, "btn_account"), callback_data="my_account")],
        [InlineKeyboardButton(get_trans(user_id, "btn_currency"), callback_data="currency_menu")],
        [InlineKeyboardButton(get_trans(user_id, "btn_support"), url=f"https://t.me/{SUPPORT_USERNAME}")]
    ]

def get_admin_menu_keyboard():
    return [
        [InlineKeyboardButton("💰 إضافة رصيد لمستخدم", callback_data="admin_add_balance"), InlineKeyboardButton("➖ خصم رصيد من مستخدم", callback_data="admin_sub_balance")],
        [InlineKeyboardButton("🔍 الاستعلام عن رصيد مستخدم", callback_data="admin_check_balance")],
        [InlineKeyboardButton("🎟 إنشاء كود هدية جديد", callback_data="admin_create_promo")],
        [InlineKeyboardButton("📢 إذاعة رسالة للجميع", callback_data="admin_broadcast"), InlineKeyboardButton("💵 تعديل نسبة الربح", callback_data="admin_set_profit")],
        [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_ban"), InlineKeyboardButton("🟢 إلغاء حظر مستخدم", callback_data="admin_unban")],
        [InlineKeyboardButton("📊 رصيد موقع SMM الأساسي", callback_data="admin_smm_balance"), InlineKeyboardButton("📈 إحصائيات البوت والمالية", callback_data="admin_stats")],
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

async def background_orders_tracker(context: ContextTypes.DEFAULT_TYPE):
    while True:
        try:
            for doc in orders_col.find():
                user_id = int(doc["user_id"])
                orders_list = doc.get("orders", [])
                updated = False

                for o in orders_list:
                    old_status = str(o.get("status", "")).strip().lower()
                    if "تم التسليم" in old_status or "ملغي" in old_status or "مكتمل جزئياً" in old_status:
                        continue

                    o_id = str(o["order_id"])
                    
                    if o_id.startswith("temp_"):
                        continue

                    try:
                        payload = {"key": SMM_API_KEY, "action": "status", "order": o_id}
                        res = await asyncio.to_thread(lambda: requests.post(SMM_API_URL, data=payload, timeout=10).json())

                        if isinstance(res, dict):
                            site_status = str(res.get("status", "")).strip().lower()
                            if not site_status:
                                site_status = str(res.get("order_status", "")).strip().lower()

                            if site_status:
                                new_translated_status = translate_status(site_status)
                                if new_translated_status != o.get("status"):
                                    o["status"] = new_translated_status
                                    updated = True

                                    if site_status in ["canceled", "cancelled"]:
                                        if not o.get("refunded", False):
                                            refund_amount = float(o.get("total_cost", 0.0))
                                            if refund_amount > 0:
                                                if user_id not in user_balances:
                                                    user_balances[user_id] = 0.0
                                                user_balances[user_id] += refund_amount
                                                save_balances()
                                            o["refunded"] = True

                                if site_status in ["completed", "complete", "success", "finished", "done"]:
                                    if not o.get("notified", False):
                                        o["notified"] = True
                                        updated = True

                                        success_msg = (
                                            f"✅ اكتمل طلبك بنجاح!\n"
                                            f"🔢 رقم الطلب: {o_id}\n"
                                            f"📦 الخدمة: {o.get('service_name', 'خدمة سوشيال ميديا')}\n"
                                            f"📊 الكمية: {o.get('qty')}\n"
                                            f"🔗 الرابط: {o.get('link')}"
                                        )
                                        for attempt in range(3):
                                            try:
                                                await context.bot.send_message(chat_id=user_id, text=success_msg, parse_mode="Markdown")
                                                break
                                            except Exception:
                                                if attempt == 2:
                                                    pass
                                                await asyncio.sleep(2)

                                        try:
                                            customer_name = "عميل مميز"
                                            try:
                                                chat_user = await context.bot.get_chat(user_id)
                                                if chat_user.first_name:
                                                    customer_name = chat_user.first_name
                                                elif chat_user.username:
                                                    customer_name = f"@{chat_user.username}"
                                            except:
                                                pass

                                            bot_info = await context.bot.get_me()
                                            channel_proof_msg = (
                                                f"⭐ **تم التسليم بنجاح** ⭐\n\n"
                                                f"👑 اسم العميل: {customer_name}\n"
                                                f"💎 الخدمة: {o.get('service_name', 'خدمة سوشيال ميديا')}\n"
                                                f"🔥 العدد: {o.get('qty')}\n"
                                                f"🔢 رقم الطلب: {o_id}\n"
                                                f"✅ الحالة: تم التسليم\n\n"
                                                f"❤️ شكراً لثقتك بنا - L.G\n\n"
                                                f"🤖 رابط البوت: https://t.me/{bot_info.username}"
                                            )
                                            for attempt in range(3):
                                                try:
                                                    await context.bot.send_message(chat_id=CHANNEL_ID, text=channel_proof_msg, parse_mode="Markdown")
                                                    break
                                                except Exception:
                                                    if attempt == 2:
                                                        pass
                                                    await asyncio.sleep(2)
                                        except Exception as channel_err:
                                            print(f"خطأ في إرسال الإثبات للقناة: {channel_err}")
                                elif site_status in ["canceled", "cancelled"]:
                                    if not o.get("cancel_notified", False):
                                        o["cancel_notified"] = True
                                        updated = True
                                        try:
                                            cancel_msg = (
                                                f"❌ تم إلغاء طلبك من الموقع وتم إسترداد الأموال بنجاح!\n"
                                                f"🔢 رقم الطلب: {o_id}\n"
                                                f"📦 الخدمة: {o.get('service_name', 'خدمة سوشيال ميديا')}\n"
                                                f"💰 المبلغ المسترد: {format_price(user_id, o.get('total_cost', 0))}"
                                            )
                                            for attempt in range(3):
                                                try:
                                                    await context.bot.send_message(chat_id=user_id, text=cancel_msg, parse_mode="Markdown")
                                                    break
                                                except Exception:
                                                    if attempt == 2:
                                                        pass
                                                    await asyncio.sleep(2)
                                        except:
                                            pass
                    except Exception as e:
                        print(f"خطأ في فحص حالة الطلب {o_id}: {e}")

                if updated:
                    orders_col.update_one({"user_id": user_id}, {"$set": {"orders": orders_list}}, upsert=True)
                    user_orders[user_id] = orders_list
        except Exception as bg_err:
            print(f"خطأ في الـ Background Worker: {bg_err}")
        
        await asyncio.sleep(60)

async def post_init(application):
    application.create_task(background_orders_tracker(application))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id in banned_users:
        if update.message:
            for attempt in range(3):
                try:
                    await update.message.reply_text("❌ عذراً، تم حظرك من استخدام هذا البوت.")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
        return

    if str(user_id) not in user_currencies_data:
        user_lang_code = (user.language_code or "").lower()
        if "ar-sa" in user_lang_code or user_lang_code == "sa":
            user_currencies_data[str(user_id)] = "SAR"
        elif "ar-jo" in user_lang_code or user_lang_code == "jo":
            user_currencies_data[str(user_id)] = "JOD"
        elif "ar-eg" in user_lang_code or user_lang_code == "eg":
            user_currencies_data[str(user_id)] = "EGP"
        elif "ar-ae" in user_lang_code or user_lang_code == "ae":
            user_currencies_data[str(user_id)] = "AED"
        elif user_lang_code.startswith("ar"):
            user_currencies_data[str(user_id)] = "EGP"
        else:
            user_currencies_data[str(user_id)] = "USD"
        save_user_currencies()

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
            for attempt in range(3):
                try:
                    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
        return

    if user_id not in user_balances:
        user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
        save_balances()

    if update.message:
        for attempt in range(3):
            try:
                await update.message.reply_text(get_trans(user_id, "main_title"), reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard(user_id)))
                break
            except Exception:
                if attempt == 2:
                    pass
                await asyncio.sleep(2)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        for attempt in range(3):
            try:
                await update.message.reply_text("❌ هذا الأمر مخصص للمشرفين فقط.")
                break
            except Exception:
                if attempt == 2:
                    pass
                await asyncio.sleep(2)
        return
    
    for attempt in range(3):
        try:
            await update.message.reply_text(
                "🛠 لوحة تحكم الأدمن:\n\nاختر العملية المطلوبة من الأزرار أدناه 👇",
                reply_markup=InlineKeyboardMarkup(get_admin_menu_keyboard())
            )
            break
        except Exception:
            if attempt == 2:
                pass
            await asyncio.sleep(2)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id

    if user_id in banned_users and user_id != ADMIN_ID:
        try:
            await query.answer("❌ تم حظرك من استخدام البوت.", show_alert=True)
        except:
            pass
        return

    if data == "exit_action":
        await query.answer()
        user_states.pop(user_id, None)
        try:
            await query.message.delete()
        except:
            for attempt in range(3):
                try:
                    await query.edit_message_text("تم إغلاق القائمة.")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
        return

    if user_id == ADMIN_ID:
        if data == "admin_add_balance":
            await query.answer()
            user_states[user_id] = {"step": "admin_waiting_add_bal"}
            for attempt in range(3):
                try:
                    await query.edit_message_text("💰 أرسل (آيدي المستخدم) و(المبلغ) المراد إضافته بهطول:\nمثال: `123456789 50`", parse_mode="Markdown")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_sub_balance":
            await query.answer()
            user_states[user_id] = {"step": "admin_waiting_sub_bal"}
            for attempt in range(3):
                try:
                    await query.edit_message_text("➖ أرسل (آيدي المستخدم) و(المبلغ) المراد خصمه بهطول:\nمثال: `123456789 20`", parse_mode="Markdown")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_check_balance":
            await query.answer()
            user_states[user_id] = {"step": "admin_waiting_check_bal"}
            for attempt in range(3):
                try:
                    await query.edit_message_text("🔍 أرسل آيدي (ID) المستخدم المراد الاستعلام عن رصيده:", parse_mode="Markdown")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_create_promo":
            await query.answer()
            user_states[user_id] = {"step": "admin_waiting_promo_details"}
            for attempt in range(3):
                try:
                    await query.edit_message_text(
                        "🎟 **إنشاء كود هدية برمجياً مع مواعيد صالحة:**\n\n"
                        "أرسل البيانات بالترتيب في رسالة واحدة:\n"
                        "`الكود` `المبلغ` `عدد الاستخدامات` `مدة الصلاحية بالساعات`\n\n"
                        "مثال:\n`FREE50 10 20 24`\n(يعني كود FREE50 بقيمة 10، لـ 20 شخص، لمدة 24 ساعة)",
                        parse_mode="Markdown"
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_broadcast":
            await query.answer()
            user_states[user_id] = {"step": "admin_waiting_broadcast"}
            for attempt in range(3):
                try:
                    await query.edit_message_text("📢 أرسل الآن الرسالة أو الإعلان الذي تريد إذاعته لكل المستخدمين:")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_set_profit":
            await query.answer()
            user_states[user_id] = {"step": "admin_waiting_profit"}
            for attempt in range(3):
                try:
                    await query.edit_message_text(f"💵 نسبة الربح الحالية هي: `{PROFIT_MARGIN}`\n\nأرسل النسبة الجديدة (مثال: `1.35` أو `1.4`):", parse_mode="Markdown")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_ban":
            await query.answer()
            user_states[user_id] = {"step": "admin_waiting_ban"}
            for attempt in range(3):
                try:
                    await query.edit_message_text("🚫 أرسل آيدي المستخدم المراد حظره:")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_unban":
            await query.answer()
            user_states[user_id] = {"step": "admin_waiting_unban"}
            for attempt in range(3):
                try:
                    await query.edit_message_text("🟢 أرسل آيدي المستخدم المراد إلغاء حظره:")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_smm_balance":
            await query.answer()
            try:
                res = await asyncio.to_thread(lambda: requests.post(SMM_API_URL, data={"key": SMM_API_KEY, "action": "balance"}, timeout=10).json())
                bal_val = res.get("balance", "غير معروف")
                curr_val = res.get("currency", "USD")
                text_smm = f"📊 **رصيد موقع SMM الأساسي:**\n\n💰 الرصيد: `{bal_val} {curr_val}`"
            except Exception as e:
                text_smm = f"❌ حدث خطأ أثناء جلب الرصيد: {e}"
            
            for attempt in range(3):
                try:
                    await query.edit_message_text(text_smm, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_menu_back")]]), parse_mode="Markdown")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_stats":
            await query.answer()
            total_users = balances_col.count_documents({})
            total_orders_count = 0
            for uid, ords in user_orders.items():
                total_orders_count += len(ords)
            
            total_money_in_wallets = sum(user_balances.values())
            
            stats_text = (
                f"📈 **إحصائيات البوت الشاملة:**\n\n"
                f"👥 إجمالي المستخدمين: `{total_users}`\n"
                f"📦 إجمالي الطلبات: `{total_orders_count}`\n"
                f"💰 إجمالي الأرصدة بالمحافظ: `{total_money_in_wallets:.2f}`\n"
                f"💵 نسبة الربح المفعلة: `{PROFIT_MARGIN}`"
            )
            for attempt in range(3):
                try:
                    await query.edit_message_text(stats_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_menu_back")]]), parse_mode="Markdown")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        elif data == "admin_menu_back":
            await query.answer()
            user_states.pop(user_id, None)
            for attempt in range(3):
                try:
                    await query.edit_message_text("🛠 لوحة تحكم الأدمن:", reply_markup=InlineKeyboardMarkup(get_admin_menu_keyboard()))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return

    if data == "currency_menu":
        await query.answer()
        user_states.pop(user_id, None)
        keyboard = []
        for code, info in CURRENCIES.items():
            keyboard.append([InlineKeyboardButton(info["name"], callback_data=f"set_curr_{code}")])
        
        keyboard.append([
            InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar"),
            InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")
        ])
        keyboard.append([InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")])
        for attempt in range(3):
            try:
                await query.edit_message_text(get_trans(user_id, "currency_title"), reply_markup=InlineKeyboardMarkup(keyboard))
                break
            except Exception:
                if attempt == 2:
                    pass
                await asyncio.sleep(2)
        return

    if data.startswith("set_curr_"):
        await query.answer()
        chosen_curr = data.replace("set_curr_", "")
        if chosen_curr in CURRENCIES:
            user_currencies_data[str(user_id)] = chosen_curr
            save_user_currencies()
            curr_name = CURRENCIES[chosen_curr]["name"]
            for attempt in range(3):
                try:
                    await query.edit_message_text(f"✅ تم تغيير العملة بنجاح إلى: {curr_name}\n\nتم تحديث الأسعار.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
        return

    if data.startswith("set_lang_"):
        await query.answer()
        chosen_lang = data.replace("set_lang_", "")
        if chosen_lang in ["ar", "en"]:
            user_langs_data[str(user_id)] = chosen_lang
            save_user_langs()
            for attempt in range(3):
                try:
                    await query.edit_message_text(get_trans(user_id, "choose_lang_done"), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
        return

    if data == "daily_gift_menu":
        if not daily_gift_cache.get("services"):
            await load_services()
        
        gift_services = daily_gift_cache.get("services")
        if not gift_services:
            await query.answer("❌ عذراً، الهدايا اليومية غير متوفرة حالياً.", show_alert=True)
            return

        claim_doc = daily_gifts_col.find_one({"user_id": user_id})
        now_time = time.time()
        if claim_doc and (now_time - claim_doc.get("last_claimed", 0) < 86400):
            remaining_time = int(86400 - (now_time - claim_doc.get("last_claimed", 0)))
            hours_rem = remaining_time // 3600
            mins_rem = (remaining_time % 3600) // 60
            await query.answer(f"⏳ لقد حصلت على الهدية اليومية بالفعل!\nيمكنك الاستلام مرة أخرى بعد: {hours_rem} ساعة و {mins_rem} دقيقة.", show_alert=True)
            return

        await query.answer()
        user_states.pop(user_id, None)
        
        keyboard = []
        for idx, srv in enumerate(gift_services):
            s_name = srv.get("name")
            if len(s_name) > 35:
                btn_txt = f"🎁 {s_name[:35]}..."
            else:
                btn_txt = f"🎁 {s_name}"
            keyboard.append([InlineKeyboardButton(btn_txt, callback_data=f"claim_gift_{idx}")])

        keyboard.extend([
            [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
            [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
        ])

        text = (
            "🎁 *الهدية اليومية المجانية*\n\n"
            "📌 *التفاصيل:*\n"
            "• الكمية: `10` (ثابتة)\n"
            "• السعر: مجاناً 100%\n"
            "• المتاح: خدمة واحدة كل 24 ساعة\n\n"
            "👇 *اختر خدمة من الأقسام المختلفة أدناه:*"
        )
        for attempt in range(3):
            try:
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                break
            except Exception:
                if attempt == 2:
                    pass
                await asyncio.sleep(2)
        return

    if data.startswith("claim_gift_"):
        claim_doc = daily_gifts_col.find_one({"user_id": user_id})
        now_time = time.time()
        if claim_doc and (now_time - claim_doc.get("last_claimed", 0) < 86400):
            remaining_time = int(86400 - (now_time - claim_doc.get("last_claimed", 0)))
            hours_rem = remaining_time // 3600
            mins_rem = (remaining_time % 3600) // 60
            await query.answer(f"⏳ لقد حصلت على الهدية اليومية بالفعل!\nيمكنك الاستلام مرة أخرى بعد: {hours_rem} ساعة و {mins_rem} دقيقة.", show_alert=True)
            return

        try:
            gift_idx = int(data.replace("claim_gift_", ""))
            gift_services = daily_gift_cache.get("services", [])
            if gift_idx >= len(gift_services):
                await query.answer("❌ هذه الخدمة غير متوفرة.", show_alert=True)
                return
            
            chosen_srv = gift_services[gift_idx]
            s_id = chosen_srv.get("service")
            
            await query.answer()
            user_states[user_id] = {"step": "waiting_daily_gift_link", "service_id": s_id}
            
            s_name = chosen_srv.get("name")
            formatted_rate = format_price(user_id, 0.0)
            
            text = (
                f"🎁 **أنت على وشك استلام الهدية:**\n\n"
                f"📌 اسم الخدمة: {s_name}\n"
                f"📊 الكمية: 10 (ثابتة)\n"
                f"💰 السعر: مجاناً ({formatted_rate})\n\n"
                f"🔗 أرسل الآن الرابط المطلوب لتنفيذ الهدية:"
            )
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="daily_gift_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="daily_gift_menu")]
            ]
            for attempt in range(3):
                try:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"خطأ في اختيار الهدية: {e}")
            await query.answer("❌ حدث خطأ ما.", show_alert=True)
        return

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
                await query.answer("❌ عذراً، هذه الخدمة لم تعد متوفرة حالياً.", show_alert=True)
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
            
            user_balances[user_id] -= total_cost
            save_balances()

            temp_order_id = f"temp_{int(time.time())}"
            if user_id not in user_orders:
                user_orders[user_id] = []
            
            user_orders[user_id].append({
                "order_id": temp_order_id,
                "service_name": selected_service.get("name"),
                "qty": qty,
                "link": link,
                "total_cost": round(total_cost, 4),
                "status": "قيد التنفيذ 🔄",
                "notified": False
            })
            save_orders_data()

            formatted_rem_bal = format_price(user_id, user_balances[user_id])
            await query.answer("✅ تم قبول وإعادة الطلب بنجاح!", show_alert=True)
            for attempt in range(3):
                try:
                    await query.edit_message_text(
                        f"✅ **تم تقديم طلب الإعادة بنجاح!**\n"
                        f"🔢 رقم الطلب (قيد المعالجة): {temp_order_id}\n"
                        f"📌 الخدمة: {selected_service.get('name')}\n"
                        f"📊 الكمية: {qty}\n"
                        f"🔗 الرابط: {link}\n"
                        f"💰 التكلفة: {format_price(user_id, total_cost)}\n"
                        f"💳 رصيدك المتبقي: {formatted_rem_bal}",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]),
                        parse_mode="Markdown"
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

            async def send_reorder_background():
                try:
                    payload = {"key": SMM_API_KEY, "action": "add", "service": s_id, "link": link, "quantity": qty}
                    res = await asyncio.to_thread(lambda: requests.post(SMM_API_URL, data=payload, timeout=15).json())
                    if "order" in res:
                        real_order_id = res["order"]
                        for ord_item in user_orders.get(user_id, []):
                            if ord_item["order_id"] == temp_order_id:
                                ord_item["order_id"] = real_order_id
                                break
                        save_orders_data()
                except Exception as bg_ex:
                    print(f"خطأ في إرسال إعادة الطلب للخلفية: {bg_ex}")

            context.application.create_task(send_reorder_background())

        except Exception as e:
            print(f"خطأ في إعادة الطلب: {e}")
            await query.answer("❌ حدث خطأ.", show_alert=True)
        return

    if data.startswith("approve_dep_") or data.startswith("reject_dep_"):
        if user_id != ADMIN_ID:
            await query.answer("❌ هذا الزر للمشرف فقط!", show_alert=True)
            return
        
        await query.answer()
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
            
            new_caption = current_caption + f"\n\n✅ حالة الطلب: تم القبول وإضافة مبلغ ({amount:.2f}) للمستخدم بنجاح."
            for attempt in range(3):
                try:
                    if query.message.photo:
                        await query.edit_message_caption(caption=new_caption, reply_markup=None)
                    else:
                        await query.edit_message_text(text=new_caption, reply_markup=None)
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            
            for attempt in range(3):
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=f"🎉 مبروك! تم قبول إيداعك بنجاح.\n\nتمت إضافة مبلغ {amount:.2f} إلى رصيدك."
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
        else:
            new_caption = current_caption + "\n\n❌ حالة الطلب: تم رفض عملية الإيداع."
            for attempt in range(3):
                try:
                    if query.message.photo:
                        await query.edit_message_caption(caption=new_caption, reply_markup=None)
                    else:
                        await query.edit_message_text(text=new_caption, reply_markup=None)
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            
            for attempt in range(3):
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text="❌ عذراً، تم رفض عملية الإيداع الخاصة بك من قبل الإدارة."
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
        return

    if data == "check_sub":
        is_subscribed = await check_user_subscription(user_id, context)
        if is_subscribed:
            await query.answer()
            if user_id not in user_balances:
                user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
                save_balances()
            for attempt in range(3):
                try:
                    await query.edit_message_text("✅ تم التحقق بنجاح!\n\nمرحباً بك في متجر الخدمات:", reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard(user_id)))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
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
            await query.answer()
            for attempt in range(3):
                try:
                    await query.edit_message_text(get_trans(user_id, "sub_check"), reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
        except:
            pass
        return

    if user_id not in user_balances:
        user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
        save_balances()

    try:
        if data == "search_service_prompt":
            await query.answer()
            user_states[user_id] = {"step": "waiting_search_query"}
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ]
            for attempt in range(3):
                try:
                    await query.edit_message_text(
                        "🔍 البحث السريع عن الخدمات:\n\nأرسل الآن كلمة مفتاحية للبحث:",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data == "promo_code_prompt":
            await query.answer()
            user_states[user_id] = {"step": "waiting_promo_code"}
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ]
            for attempt in range(3):
                try:
                    await query.edit_message_text("🎟 **شحن كود هدية:**\n\nأرسل الآن كود الهدية أو القسيمة لإضافته إلى رصيدك:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data == "my_account":
            await query.answer()
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
            for attempt in range(3):
                try:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data == "payment_methods":
            await query.answer()
            user_states.pop(user_id, None)
            text = "💳 اختر طريقة الشحن المناسبة لك:"
            keyboard = [
                [InlineKeyboardButton("📞 شحن عبر فودافون كاش", callback_data="pay_vodafone")],
                [InlineKeyboardButton("🪙 شحن عبر USDT (TRC-20)", callback_data="pay_usdt")],
                [InlineKeyboardButton("⚡ شحن تلقائي فوري (قريباً عبر بوابة الدفع)", callback_data="auto_pay_info")],
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ]
            for attempt in range(3):
                try:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data == "auto_pay_info":
            await query.answer("⚡ جاري تفعيل بوابات الدفع التلقائي الفوري بالتعاون مع المزودين قريباً!", show_alert=True)
            return

        elif data == "pay_vodafone":
            await query.answer()
            user_states[user_id] = {"step": "deposit_waiting_screenshot", "method": "فودافون كاش"}
            text = f"📞 تحويل على رقم: {VODAFONE_WALLET}\nاسم الحساب: {WALLET_NAME}\n\n📸 أرسل صورة الإيصال (اسكرين شوت):"
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="payment_methods")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="payment_methods")]
            ]
            for attempt in range(3):
                try:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data == "pay_usdt":
            await query.answer()
            user_states[user_id] = {"step": "deposit_waiting_screenshot", "method": "USDT (TRC20)"}
            text = f"🪙 عنوان المحفظة:\n{USDT_TRC20_WALLET}\n\n📸 أرسل صورة الإيصال (اسكرين شوت):"
            keyboard = [
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="payment_methods")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="payment_methods")]
            ]
            for attempt in range(3):
                try:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data == "my_favorites":
            await query.answer()
            user_states.pop(user_id, None)
            favs = user_favorites.get(user_id, [])
            if not favs:
                keyboard = [
                    [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                    [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
                ]
                for attempt in range(3):
                    try:
                        await query.edit_message_text("⭐ ليس لديك أي خدمات في المفضلة.", reply_markup=InlineKeyboardMarkup(keyboard))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return

            keyboard = []
            for s_id in favs:
                found_name = f"خدمة رقم {s_id}"
                for cat in cached_subcategories:
                    for sub_c in cached_subcategories[cat]:
                        for s in cached_subcategories[cat][sub_c]:
                            if str(s.get('service')) == str(s_id):
                                found_name = s.get('name')
                                break
                
                if len(found_name) > 35:
                    btn_txt = f"❤️ {found_name[:35]}..."
                else:
                    btn_txt = f"❤️ {found_name}"
                keyboard.append([
                    InlineKeyboardButton(btn_txt, callback_data=f"srv_{s_id}")
                ])

            keyboard.extend([
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ])
            for attempt in range(3):
                try:
                    await query.edit_message_text("⭐ خدماتك المفضلة:", reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data.startswith("fav_toggle_favs__"):
            s_id = data.replace("fav_toggle_favs__", "")
            if user_id in user_favorites:
                user_favorites[user_id] = [x for x in user_favorites[user_id] if str(x) != str(s_id)]
                save_favorites_data()
            await query.answer("❌ تم إزالة الخدمة من المفضلة.", show_alert=False)
            
            favs = user_favorites.get(user_id, [])
            if not favs:
                keyboard = [
                    [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                    [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
                ]
                for attempt in range(3):
                    try:
                        await query.edit_message_text("⭐ ليس لديك أي خدمات في المفضلة.", reply_markup=InlineKeyboardMarkup(keyboard))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return

            keyboard = []
            for s_id_item in favs:
                found_name = f"خدمة رقم {s_id_item}"
                for cat in cached_subcategories:
                    for sub_c in cached_subcategories[cat]:
                        for s in cached_subcategories[cat][sub_c]:
                            if str(s.get('service')) == str(s_id_item):
                                found_name = s.get('name')
                                break
                if len(found_name) > 35:
                    btn_txt = f"❤️ {found_name[:35]}..."
                else:
                    btn_txt = f"❤️ {found_name}"
                keyboard.append([
                    InlineKeyboardButton(btn_txt, callback_data=f"srv_{s_id_item}")
                ])

            keyboard.extend([
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ])
            for attempt in range(3):
                try:
                    await query.edit_message_text("⭐ خدماتك المفضلة:", reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return

        elif data == "my_orders":
            await query.answer()
            user_states.pop(user_id, None)
            
            orders = user_orders.get(user_id, [])
            if not orders:
                keyboard = [
                    [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                    [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
                ]
                for attempt in range(3):
                    try:
                        await query.edit_message_text("📦 ليس لديك أي طلبات سابقة.", reply_markup=InlineKeyboardMarkup(keyboard))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return

            text_orders = "📦 طلباتك السابقة:\n\n"
            keyboard = []

            for idx, order in enumerate(orders[-10:], 1):
                o_id = order.get('order_id')
                status_str = translate_status(order.get('status', 'قيد التنفيذ 🔄'))

                formatted_cost = format_price(user_id, order.get('total_cost', 0))
                text_orders += (
                    f"--- الطلب #{idx} ---\n"
                    f"📌 الخدمة: {order.get('service_name', 'غير معروف')}\n"
                    f"🆔 رقم الطلب: {o_id}\n"
                    f"📊 الكمية: {order.get('qty', '-')}\n"
                    f"💰 التكلفة: {formatted_cost}\n"
                    f"📌 الحالة: {status_str}\n\n"
                )
                keyboard.append([InlineKeyboardButton(f"🔄 {idx} إعادة طلب رقم {o_id}", callback_data=f"reorder_{o_id}")])

            keyboard.extend([
                [InlineKeyboardButton("🔄 تحديث العرض", callback_data="my_orders")],
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="main_menu")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="main_menu")]
            ])
            for attempt in range(3):
                try:
                    await query.edit_message_text(text_orders, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data == "show_categories":
            await query.answer()
            user_states.pop(user_id, None)
            if not cached_subcategories: 
                await load_services()
            
            keyboard = [
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
            for attempt in range(3):
                try:
                    await query.edit_message_text(get_trans(user_id, "sub_title"), reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data.startswith("platform_"):
            await query.answer()
            platform_name = data.replace("platform_", "")
            sub_dict = cached_subcategories.get(platform_name, {})
            
            keyboard = []
            for sub_cat_name in sub_dict:
                count_s = len(sub_dict[sub_cat_name])
                if count_s > 0:
                    sub_key_id = subcat_keys_map.get(f"{platform_name}__{sub_cat_name}", "1")
                    keyboard.append([InlineKeyboardButton(f"📂 {sub_cat_name} ({count_s})", callback_data=f"subcat_{sub_key_id}__0")])
            
            keyboard.extend([
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data="show_categories")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data="show_categories")]
            ])
            for attempt in range(3):
                try:
                    await query.edit_message_text(f"أقسام خدمات {platform_name}:", reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data.startswith("subcat_"):
            await query.answer()
            parts = data.split("__")
            sub_key_id = parts[0].replace("subcat_", "")
            page = int(parts[1])
            
            mapped_data = subcat_keys_map.get(sub_key_id)
            if not mapped_data:
                await query.answer("❌ عذراً، انتهت صلاحية الجلسة، أعد اختيار القسم.", show_alert=True)
                return
                
            platform_name, sub_cat_name = mapped_data
            
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
                
                is_fav = str(s_id) in [str(x) for x in user_favorites.get(user_id, [])]
                fav_icon = "❤️" if is_fav else "⭐"
                
                if len(s_name) > 35:
                    btn_text = f"{fav_icon} {s_name[:35]}..."
                else:
                    btn_text = f"{fav_icon} {s_name}"
                
                keyboard.append([
                    InlineKeyboardButton(btn_text, callback_data=f"srv_{s_id}")
                ])
                
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"subcat_{sub_key_id}__{page - 1}"))
            if page < max_pages:
                nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"subcat_{sub_key_id}__{page + 1}"))
            
            if nav_buttons:
                keyboard.append(nav_buttons)
                
            keyboard.extend([
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data=f"platform_{platform_name}")],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data=f"platform_{platform_name}")]
            ])
            
            text_msg = f"خدمات {platform_name} 🏷 ({sub_cat_name})\nصفحة {page + 1} من {max_pages + 1}" if services_in_sub else f"❌ لا توجد خدمات في هذا القسم."
            for attempt in range(3):
                try:
                    await query.edit_message_text(text_msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data.startswith("srv_fav_toggle_"):
            s_id = data.replace("srv_fav_toggle_", "")
            if user_id not in user_favorites:
                user_favorites[user_id] = []
            
            user_favs_str = [str(x) for x in user_favorites[user_id]]
            if str(s_id) in user_favs_str:
                user_favorites[user_id] = [x for x in user_favorites[user_id] if str(x) != str(s_id)]
                await query.answer("❌ تم إزالة الخدمة من المفضلة.", show_alert=False)
            else:
                user_favorites[user_id].append(s_id)
                await query.answer("⭐ تم إضافة الخدمة إلى المفضلة بنجاح!", show_alert=False)
            save_favorites_data()

            selected_service = None
            back_target = "show_categories"
            
            for cat in cached_subcategories:
                for sub_c in cached_subcategories[cat]:
                    for s in cached_subcategories[cat][sub_c]:
                        if str(s.get("service")) == str(s_id):
                            selected_service = s
                            sub_key_id = subcat_keys_map.get(f"{cat}__{sub_c}", "1")
                            back_target = f"subcat_{sub_key_id}__0"
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
            
            is_fav = str(s_id) in [str(x) for x in user_favorites.get(user_id, [])]
            fav_btn_text = "❌ إزالة من المفضلة" if is_fav else "⭐ إضافة إلى المفضلة"
            
            keyboard = [
                [InlineKeyboardButton(fav_btn_text, callback_data=f"srv_fav_toggle_{s_id}")],
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data=back_target)],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data=back_target)]
            ]
            for attempt in range(3):
                try:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return

        elif data.startswith("srv_"):
            await query.answer()
            s_id = data.replace("srv_", "")
            selected_service = None
            back_target = "show_categories"
            
            for cat in cached_subcategories:
                for sub_c in cached_subcategories[cat]:
                    for s in cached_subcategories[cat][sub_c]:
                        if str(s.get("service")) == str(s_id):
                            selected_service = s
                            sub_key_id = subcat_keys_map.get(f"{cat}__{sub_c}", "1")
                            back_target = f"subcat_{sub_key_id}__0"
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
            
            is_fav = str(s_id) in [str(x) for x in user_favorites.get(user_id, [])]
            fav_btn_text = "❌ إزالة من المفضلة" if is_fav else "⭐ إضافة إلى المفضلة"
            
            keyboard = [
                [InlineKeyboardButton(fav_btn_text, callback_data=f"srv_fav_toggle_{s_id}")],
                [InlineKeyboardButton(get_trans(user_id, "exit"), callback_data="exit_action"), InlineKeyboardButton(get_trans(user_id, "back"), callback_data=back_target)],
                [InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu"), InlineKeyboardButton(get_trans(user_id, "back_step"), callback_data=back_target)]
            ]
            for attempt in range(3):
                try:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

        elif data == "main_menu":
            await query.answer()
            user_states.pop(user_id, None)
            try:
                for attempt in range(3):
                    try:
                        await query.edit_message_text(
                            get_trans(user_id, "main_title"), 
                            reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard(user_id))
                        )
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            except:
                for attempt in range(3):
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=get_trans(user_id, "main_title"),
                            reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard(user_id))
                        )
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)

    except Exception as e:
        print(f"خطأ في button_handler: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in banned_users and user_id != ADMIN_ID:
        return

    if user_id == ADMIN_ID and user_id in user_states:
        state_data = user_states[user_id]
        step = state_data.get("step")
        
        if step == "admin_waiting_add_bal":
            user_states.pop(user_id, None)
            try:
                parts = update.message.text.strip().split()
                target_uid = int(parts[0])
                amount = float(parts[1])
                
                if target_uid not in user_balances:
                    user_balances[target_uid] = 0.0
                user_balances[target_uid] += amount
                save_balances()
                
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"✅ تمت إضافة مبلغ `{amount}` بنجاح للمستخدم `{target_uid}`.", parse_mode="Markdown")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                try:
                    for attempt in range(3):
                        try:
                            await context.bot.send_message(target_uid, f"🎁 قامت الإدارة بإضافة مبلغ `{amount}` إلى رصيدك!")
                            break
                        except Exception:
                            if attempt == 2:
                                pass
                            await asyncio.sleep(2)
                except:
                    pass
            except Exception as e:
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"❌ خطأ في الإدخال: {e}\nالصيغة الصحيحة: `ID المبلغ`")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            return

        elif step == "admin_waiting_sub_bal":
            user_states.pop(user_id, None)
            try:
                parts = update.message.text.strip().split()
                target_uid = int(parts[0])
                amount = float(parts[1])
                
                if target_uid not in user_balances:
                    user_balances[target_uid] = 0.0
                user_balances[target_uid] = max(0.0, user_balances[target_uid] - amount)
                save_balances()
                
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"✅ تمت خصم مبلغ `{amount}` بنجاح من المستخدم `{target_uid}`.", parse_mode="Markdown")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                try:
                    for attempt in range(3):
                        try:
                            await context.bot.send_message(target_uid, f"⚠️ قامت الإدارة بخصم مبلغ `{amount}` من رصيدك.")
                            break
                        except Exception:
                            if attempt == 2:
                                pass
                            await asyncio.sleep(2)
                except:
                    pass
            except Exception as e:
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"❌ خطأ في الإدخال: {e}\nالصيغة الصحيحة: `ID المبلغ`")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            return

        elif step == "admin_waiting_check_bal":
            user_states.pop(user_id, None)
            try:
                target_uid = int(update.message.text.strip())
                user_bal = user_balances.get(target_uid, 0.0)
                for attempt in range(3):
                    try:
                        await update.message.reply_text(
                            f"🔍 **نتيجة الاستعلام عن المستخدم:**\n\n"
                            f"🆔 الآيدي: `{target_uid}`\n"
                            f"💰 عدد النقاط أو الرصيد: `{user_bal:.2f}`",
                            parse_mode="Markdown"
                        )
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            except Exception as e:
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"❌ خطأ في الآيدي المدخل: {e}\nيرجى إرسال أرقام صحيحة فقط.")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            return

        elif step == "admin_waiting_promo_details":
            user_states.pop(user_id, None)
            try:
                parts = update.message.text.strip().split()
                code_str = parts[0].upper()
                amount_val = float(parts[1])
                max_uses = int(parts[2])
                hours_valid = int(parts[3])
                
                expires_at = time.time() + (hours_valid * 3600)
                
                promo_codes_col.update_one(
                    {"code": code_str},
                    {
                        "$set": {
                            "amount": amount_val,
                            "max_uses": max_uses,
                            "used_count": 0,
                            "expires_at": expires_at,
                            "used_by": []
                        }
                    },
                    upsert=True
                )
                
                for attempt in range(3):
                    try:
                        await update.message.reply_text(
                            f"✅ **تم إنشاء كود الهدية بنجاح!**\n\n"
                            f"🎟 الكود: `{code_str}`\n"
                            f"💰 القيمة: `{amount_val}`\n"
                            f"👥 الحد الأقصى للاستخدام: `{max_uses}`\n"
                            f"⏳ صلاحية الوقت: `{hours_valid} ساعة`",
                            parse_mode="Markdown"
                        )
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            except Exception as e:
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"❌ خطأ في صياغة البيانات:\n{e}\n\nالصيغة الصحيحة: `الكود المبلغ عدد_الاستخدامات ساعات_الصلاحية`")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            return

        elif step == "admin_waiting_broadcast":
            user_states.pop(user_id, None)
            bc_text = update.message.text
            all_users = list(user_balances.keys())
            success_count = 0
            
            status_msg = await update.message.reply_text("⏳ جاري إرسال الإذاعة لكل المستخدمين...")
            for uid in all_users:
                try:
                    for attempt in range(3):
                        try:
                            await context.bot.send_message(chat_id=uid, text=bc_text)
                            break
                        except Exception:
                            if attempt == 2:
                                pass
                            await asyncio.sleep(2)
                    success_count += 1
                except:
                    pass
            try:
                for attempt in range(3):
                    try:
                        await status_msg.edit_text(f"✅ تم بنجاح إرسال الإذاعة إلى `{success_count}` مستخدم.")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            except:
                pass
            return

        elif step == "admin_waiting_profit":
            user_states.pop(user_id, None)
            global PROFIT_MARGIN
            try:
                new_margin = float(update.message.text.strip())
                PROFIT_MARGIN = new_margin
                save_settings(new_margin)
                await load_services() 
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"✅ تم تحديث نسبة الربح بنجاح إلى: `{PROFIT_MARGIN}` وتم إعادة تحميل أسعار الخدمات.", parse_mode="Markdown")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            except Exception as e:
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"❌ خطأ في القيمة المدخلة: {e}")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            return

        elif step == "admin_waiting_ban":
            user_states.pop(user_id, None)
            try:
                target_uid = int(update.message.text.strip())
                banned_users.add(target_uid)
                save_banned_db(target_uid, True)
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"✅ تم حظر المستخدم `{target_uid}` بنجاح.", parse_mode="Markdown")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            except Exception as e:
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"❌ حدث خطأ: {e}")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            return

        elif step == "admin_waiting_unban":
            user_states.pop(user_id, None)
            try:
                target_uid = int(update.message.text.strip())
                if target_uid in banned_users:
                    banned_users.remove(target_uid)
                save_banned_db(target_uid, False)
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"✅ تم إلغاء حظر المستخدم `{target_uid}` بنجاح.", parse_mode="Markdown")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            except Exception as e:
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"❌ حدث خطأ: {e}")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            return

    if user_id in user_states and user_states[user_id].get("step") == "deposit_waiting_screenshot":
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            user_states[user_id]["screenshot"] = photo_file_id
            user_states[user_id]["step"] = "deposit_waiting_phone"
            for attempt in range(3):
                try:
                    await update.message.reply_text("📱 الخطوة 2: أرسل رقم الهاتف المرسل منه (يجب أن يبدأ بـ 01 ويتكون من 11 رقماً):")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return
        else:
            for attempt in range(3):
                try:
                    await update.message.reply_text("❌ يرجى إرسال صورة الإيصال كصورة صحيحة:")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return

    if not update.message.text:
        return
        
    text = update.message.text.strip()
    
    if user_id in user_states:
        state_data = user_states[user_id]
        step = state_data.get("step")
        
        if step == "waiting_promo_code":
            user_states.pop(user_id, None)
            entered_code = text.upper()
            
            promo_doc = promo_codes_col.find_one({"code": entered_code})
            if not promo_doc:
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ عذراً، هذا الكود غير صحيح أو غير موجود.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            current_time = time.time()
            if current_time > promo_doc.get("expires_at", 0):
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ عذراً، لقد انتهت صلاحية هذا الكود (انتهى وقت الموعد المحدد).", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            if promo_doc.get("used_count", 0) >= promo_doc.get("max_uses", 0):
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ عذراً، لقد استنفد هذا الكود الحد الأقصى لعدد الاستخدامات.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            used_by_list = promo_doc.get("used_by", [])
            if user_id in used_by_list:
                for attempt in range(3):
                    try:
                        await update.message.reply_text("⚠️ لقد قمت باستخدام هذا الكود مسبقاً ولا يمكنك استخدامه مرتين.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            promo_amount = float(promo_doc.get("amount", 0))
            if user_id not in user_balances:
                user_balances[user_id] = 0.0
            user_balances[user_id] += promo_amount
            save_balances()
            
            promo_codes_col.update_one(
                {"code": entered_code},
                {
                    "$inc": {"used_count": 1},
                    "$push": {"used_by": user_id}
                }
            )
            
            formatted_bal = format_price(user_id, user_balances[user_id])
            for attempt in range(3):
                try:
                    await update.message.reply_text(
                        f"🎉 مبروك! تم شحن الكود بنجاح.\n\n"
                        f"💰 تمت إضافة مبلغ: `{promo_amount}` إلى رصيدك.\n"
                        f"💳 رصيدك الحالي: {formatted_bal}",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]),
                        parse_mode="Markdown"
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return

        elif step == "waiting_daily_gift_link":
            user_states.pop(user_id, None)
            s_id = state_data.get("service_id")
            link = text
            qty = 10 

            gift_services = daily_gift_cache.get("services", [])
            selected_gift_srv = None
            for srv_item in gift_services:
                if str(srv_item.get("service")) == str(s_id):
                    selected_gift_srv = srv_item
                    break

            if not selected_gift_srv:
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ عذراً، انتهت صلاحية الهدية أو حدث خطأ، أعد المحاولة.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return

            daily_gifts_col.update_one(
                {"user_id": user_id},
                {"$set": {"last_claimed": time.time()}},
                upsert=True
            )

            temp_order_id = f"temp_gift_{int(time.time())}"
            if user_id not in user_orders: user_orders[user_id] = []
            user_orders[user_id].append({
                "order_id": temp_order_id, 
                "service_name": f"[هدية يومية] {selected_gift_srv.get('name')}", 
                "qty": qty, 
                "link": link,
                "total_cost": 0.0,
                "status": "قيد التنفيذ 🔄",
                "notified": False
            })
            save_orders_data()
            
            for attempt in range(3):
                try:
                    await update.message.reply_text(
                        f"🎁 **تم إرسال هدكتك اليومية بنجاح!**\n\n"
                        f"🔢 رقم الطلب (قيد المعالجة): `{temp_order_id}`\n"
                        f"📊 الكمية: `{qty}`\n"
                        f"🔗 الرابط: `{link}`\n"
                        f"✅ مبروك! يمكنك استلام هدية جديدة بعد 24 ساعة.",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]),
                        parse_mode="Markdown"
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

            async def send_gift_api_background():
                try:
                    payload = {"key": SMM_API_KEY, "action": "add", "service": s_id, "link": link, "quantity": qty}
                    res = await asyncio.to_thread(lambda: requests.post(SMM_API_URL, data=payload, timeout=15).json())
                    if "order" in res:
                        real_order_id = res["order"]
                        for ord_item in user_orders.get(user_id, []):
                            if ord_item["order_id"] == temp_order_id:
                                ord_item["order_id"] = real_order_id
                                break
                        save_orders_data()
                except Exception as bg_e:
                    print(f"خطأ في إرسال الهدية للخلفية: {bg_e}")

            context.application.create_task(send_gift_api_background())
            return

        elif step == "deposit_waiting_phone":
            if not (text.isdigit() and text.startswith("01") and len(text) == 11):
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ رقم الهاتف غير صحيح. يجب أن يبدأ الرقم بـ 01 ويتكون من 11 رقماً:\nأرسل رقم الهاتف الصحيح:")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
            user_states[user_id]["phone"] = text
            user_states[user_id]["step"] = "deposit_waiting_amount"
            for attempt in range(3):
                try:
                    await update.message.reply_text("💰 الخطوة 3: أرسل المبلغ الذي تم تحويله (أرقام فقط):")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return

        elif step == "deposit_waiting_amount":
            if not text.replace(".", "", 1).isdigit():
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ المبلغ غير صحيح. يجب أن يتكون المبلغ من أرقام فقط:\nأرسل المبلغ الصحيح:")
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
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
                f"📱 الهاتف: {phone}\n"
                f"💰 المبلغ: {numeric_amount}"
            )
            amount_str_for_cb = str(numeric_amount).replace(".", "_")
            keyboard = [
                [
                    InlineKeyboardButton("✅ قبول", callback_data=f"approve_dep__{user_id}__{amount_str_for_cb}"),
                    InlineKeyboardButton("❌ رفض", callback_data=f"reject_dep__{user_id}__{amount_str_for_cb}")
                ]
            ]
            
            try:
                for attempt in range(3):
                    try:
                        await context.bot.send_photo(
                            chat_id=ADMIN_ID,
                            photo=screenshot,
                            caption=admin_msg,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            except:
                for attempt in range(3):
                    try:
                        await context.bot.send_message(
                            chat_id=ADMIN_ID,
                            text=admin_msg + "\n\n(فشل إرسال الصورة)",
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
            
            for attempt in range(3):
                try:
                    await update.message.reply_text(
                        "✅ تم إرسال طلب الشحن بنجاح إلى الإدارة، سيتم مراجعته وإضافة الرصيد في أقرب وقت.",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]])
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return

        elif step == "waiting_search_query":
            user_states.pop(user_id, None)
            q = text.lower()
            matching_services = []
            
            for cat in cached_subcategories:
                for sub_c in cached_subcategories[cat]:
                    for s in cached_subcategories[cat][sub_c]:
                        if q in s.get("name", "").lower() or q in str(s.get("service", "")):
                            matching_services.append(s)
            
            if not matching_services:
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ لم يتم العثور على أي خدمات تطابق بحثك.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            keyboard = []
            for s in matching_services[:10]:
                s_id = s.get("service")
                s_name = s.get("name", "")
                if len(s_name) > 35:
                    btn_text = f"⭐ {s_name[:35]}..."
                else:
                    btn_text = f"⭐ {s_name}"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"srv_{s_id}")])
                
            keyboard.append([InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")])
            for attempt in range(3):
                try:
                    await update.message.reply_text(f"🔍 نتائج البحث عن: `{text}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return

        elif step == "waiting_quantity":
            s_id = state_data.get("service_id")
            back_target = state_data.get("cat_back", "show_categories")
            user_states.pop(user_id, None)
            
            if not text.isdigit():
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ الكمية غير صحيحة. يجب أن تكون أرقاماً فقط:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "back"), callback_data=f"srv_{s_id}")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            qty = int(text)
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
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ عذراً، هذه الخدمة غير متوفرة حالياً.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            min_q = int(selected_service.get("min", 10))
            max_q = int(selected_service.get("max", 10000))
            
            if qty < min_q or qty > max_q:
                for attempt in range(3):
                    try:
                        await update.message.reply_text(f"❌ الكمية المدخلة خارج الحد الأدنى ({min_q}) والحد الأقصى ({max_q}).", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "back"), callback_data=f"srv_{s_id}")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            rate = float(selected_service.get("client_rate", 0))
            total_cost = (qty / 1000) * rate
            
            if user_balances.get(user_id, 0.0) < total_cost:
                for attempt in range(3):
                    try:
                        await update.message.reply_text(
                            f"❌ رصيدك الحالي غير كافٍ لإتمام هذا الطلب!\n\n"
                            f"💰 التكلفة المطلوبة: {format_price(user_id, total_cost)}\n"
                            f"💳 رصيدك الحالي: {format_price(user_id, user_balances.get(user_id, 0.0))}",
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 شحن الرصيد", callback_data="payment_methods"), InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]])
                        )
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            user_states[user_id] = {"step": "waiting_link", "service_id": s_id, "qty": qty, "total_cost": total_cost, "cat_back": back_target}
            for attempt in range(3):
                try:
                    await update.message.reply_text(
                        f"🔗 أرسل الآن الرابط المطلوب للخدمة:\n\n"
                        f"📌 الخدمة: {selected_service.get('name')}\n"
                        f"📊 الكمية: {qty}\n"
                        f"💰 التكلفة: {format_price(user_id, total_cost)}",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "back"), callback_data=f"srv_{s_id}")]])
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)
            return

        elif step == "waiting_link":
            s_id = state_data.get("service_id")
            qty = state_data.get("qty")
            total_cost = state_data.get("total_cost")
            link = text
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
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ حدث خطأ، الخدمة غير متوفرة.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            if user_balances.get(user_id, 0.0) < total_cost:
                for attempt in range(3):
                    try:
                        await update.message.reply_text("❌ رصيدك غير كافٍ.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]))
                        break
                    except Exception:
                        if attempt == 2:
                            pass
                        await asyncio.sleep(2)
                return
                
            user_balances[user_id] -= total_cost
            save_balances()
            
            temp_order_id = f"temp_{int(time.time())}"
            if user_id not in user_orders:
                user_orders[user_id] = []
            
            user_orders[user_id].append({
                "order_id": temp_order_id,
                "service_name": selected_service.get("name"),
                "qty": qty,
                "link": link,
                "total_cost": round(total_cost, 4),
                "status": "قيد التنفيذ 🔄",
                "notified": False
            })
            save_orders_data()
            
            formatted_rem_bal = format_price(user_id, user_balances[user_id])
            for attempt in range(3):
                try:
                    await update.message.reply_text(
                        f"✅ **تم إرسال طلبك بنجاح!**\n\n"
                        f"🔢 رقم الطلب (قيد المعالجة): `{temp_order_id}`\n"
                        f"📌 الخدمة: {selected_service.get('name')}\n"
                        f"📊 الكمية: {qty}\n"
                        f"🔗 الرابط: {link}\n"
                        f"💰 التكلفة الإجمالية: {format_price(user_id, total_cost)}\n"
                        f"💳 رصيدك المتبقي: {formatted_rem_bal}",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_trans(user_id, "main_menu_btn"), callback_data="main_menu")]]),
                        parse_mode="Markdown"
                    )
                    break
                except Exception:
                    if attempt == 2:
                        pass
                    await asyncio.sleep(2)

            async def send_order_to_api_background():
                try:
                    payload = {"key": SMM_API_KEY, "action": "add", "service": s_id, "link": link, "quantity": qty}
                    res = await asyncio.to_thread(lambda: requests.post(SMM_API_URL, data=payload, timeout=15).json())
                    if "order" in res:
                        real_order_id = res["order"]
                        for ord_item in user_orders.get(user_id, []):
                            if ord_item["order_id"] == temp_order_id:
                                ord_item["order_id"] = real_order_id
                                break
                        save_orders_data()
                except Exception as bg_e:
                    print(f"خطأ في إرسال الطلب للخلفية: {bg_e}")

            context.application.create_task(send_order_to_api_background())
            return

def main():
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
