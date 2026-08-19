import json
import os
import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

# --- الإعدادات ---
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

logging.basicConfig(level=logging.INFO)
cached_categories = {}
free_services = {} 
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

def save_balances():
    save_json_file(BALANCES_FILE, user_balances)

def save_orders_data():
    save_json_file(ORDERS_FILE, user_orders)

def check_site_balance():
    try:
        response = requests.post(SMM_API_URL, data={"key": SMM_API_KEY, "action": "balance"}, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            balance = float(res_data.get("balance", 0.0))
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
    global cached_categories, free_services
    try:
        response = requests.post(SMM_API_URL, data={"key": SMM_API_KEY, "action": "services"}, timeout=15)
        if response.status_code == 200:
            services_list = response.json()
            temp = {}
            temp_free = []
            
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
        [InlineKeyboardButton("🎁 الرشق اليومي المجاني", callback_data="free_section")],
        [InlineKeyboardButton("📦 طلباتي السابقة وحالتها", callback_data="my_orders")],
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    site_balance = check_site_balance()
    if site_balance <= 0 and user_id != ADMIN_ID:
        maintenance_text = "⚠️ **البوت متوقف حالياً للصيانة أو تحديث الخدمات.**\n\nيرجى المحاولة في وقت لاحق وشكراً لتفهمكم ❤️"
        if update.message:
            await update.message.reply_text(maintenance_text, parse_mode="Markdown")
        return

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
            await query.edit_message_text("✅ تم التحقق بنجاح!\n\nمرحباً بك في متجر الخدمات:", reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard()))
        else:
            await query.answer("❌ لم تقم بالاشتراك في القناة بعد!", show_alert=True)
        return

    is_subscribed = await check_user_subscription(user_id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("📢 اشترك في قناة الإثباتات", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ اشتركت، تحقق من الاشتراكات", callback_data="check_sub")]
        ]
        await query.edit_message_text("⚠️ يجب الاشتراك في القناة أولاً لاستخدام البوت.", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if user_id not in user_balances:
        user_balances[user_id] = 300.0 if user_id == ADMIN_ID else 0.0
        save_balances()

    if data == "admin_panel":
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
            f"📊 **إحصائيات البوت:**\n\n👥 عدد المستخدمين: `{total_users}`\n💰 رصيد الموقع الحالي: `{site_balance}`",
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
                keyboard.append([InlineKeyboardButton(f"📱 خدمات {p}", callback_data=f"plat_{p}_0")])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")])
        await query.edit_message_text("🔥 **اختر المنصة المطلوبة:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

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
        
        desc_text = "🎁 **قسم الرشق اليومي المجاني:**\n\n👇 اختر الخدمة المجانية المتاحة حالياً للطلب الفوري:"
        await query.edit_message_text(desc_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "main_menu":
        user_states.pop(user_id, None)
        await query.edit_message_text("✨ **القائمة الرئيسية:**", reply_markup=InlineKeyboardMarkup(get_main_menu_keyboard()), parse_mode="Markdown")

    elif data == "my_orders":
        user_states.pop(user_id, None)
        user_list_orders = user_orders.get(user_id, [])
        
        if not user_list_orders:
            keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]]
            await query.edit_message_text("📦 **سجل طلباتك:**\n\nعذراً، ليس لديك أي طلبات سابقة مسجلة حتى الآن.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            return

        recent_orders = user_list_orders[-5:]
        orders_text = "📦 **آخر طلباتك وحالتها الحالية:**\n"
        
        try:
            payload = {
                "key": SMM_API_KEY,
                "action": "multi_status",
                "orders": ",".join([str(o["order_id"]) for o in recent_orders])
            }
            res = requests.post(SMM_API_URL, data=payload, timeout=10).json()
            
            for o in recent_orders:
                o_id = str(o["order_id"])
                status_info = res.get(o_id, {})
                status_text = status_info.get("status", "قيد المعالجة / جاري التحقق")
                
                status_map = {
                    "Completed": "مكتملة ✅",
                    "Pending": "قيد الانتظار ⏳",
                    "Processing": "قيد التنفيذ 🔄",
                    "In progress": "قيد التنفيذ 🔄",
                    "Partial": "ملغي جزئياً ⚠️",
                    "Canceled": "ملغاة ❌"
                }
                translated_status = status_map.get(status_text, status_text)
                
                orders_text += f"\n🆔 رقم الطلب: `{o_id}`\n📌 الخدمة: {o['service_name']}\n📊 الكمية: {o['qty']}\n⚡ الحالة: **{translated_status}**\n------------------"
        except Exception as e:
            print(f"خطأ في جلب حالات الطلبات: {e}")
            for o in recent_orders:
                orders_text += f"\n🆔 رقم الطلب: `{o['order_id']}`\n📌 الخدمة: {o['service_name']}\n------------------"

        keyboard = [[InlineKeyboardButton("🔄 تحديث القائمة", callback_data="my_orders")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]]
        
        await query.edit_message_text(orders_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "vodafone_info":
        user_states[user_id] = {"step": "deposit_waiting_amount"}
        text = (
            f"💳 **خطوات شحن الرصيد عبر فودافون كاش:**\n\n"
            f"رقم المحفظة: `{VODAFONE_WALLET}`\n"
            f"اسم الحساب: {WALLET_NAME}\n\n"
            "📥 **الخطوة 1/3:**\nأرسل الآن **المبلغ المرسل** بالأرقام (مثال: `50`):"
        )
        keyboard = [[InlineKeyboardButton("🔙 إلغاء والرجوع", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "my_account":
        balance = user_balances.get(user_id, 0.0)
        text = f"👤 **معلومات حسابك:**\n\n🆔 الآيدي: `{user_id}`\n💰 رصيدك الحالي: **{balance:.2f} جنيه**"
        keyboard = [[InlineKeyboardButton("📦 سجل طلباتي", callback_data="my_orders")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("approve_"):
        if user_id != ADMIN_ID: return
        parts = data.split("_")
        target_user = int(parts[1])
        amount = float(parts[2])

        if target_user not in user_balances:
            user_balances[target_user] = 0.0
        user_balances[target_user] += amount
        save_balances()

        try:
            await context.bot.send_message(
                chat_id=target_user,
                text=f"✅ **تم قبول عملية الشحن بنجاح!**\n\nتمت إضافة `{amount}` جنيه إلى رصيدك. شكراً لاستخدامك خدماتنا 🎉",
                parse_mode="Markdown"
            )
        except Exception:
            pass

        await query.edit_message_caption(caption=query.message.caption + "\n\n**[✅ تم قبول الطلب وإضافة الرصيد]**", reply_markup=None)

    elif data.startswith("reject_"):
        if user_id != ADMIN_ID: return
        parts = data.split("_")
        target_user = int(parts[1])

        try:
            await context.bot.send_message(
                chat_id=target_user,
                text="❌ **عذراً، تم رفض إيصال الشحن من قبل الإدارة.**\nيرجى التأكد من البيانات وإعادة المحاولة أو التواصل مع الدعم.",
                parse_mode="Markdown"
            )
        except Exception:
            pass

        await query.edit_message_caption(caption=query.message.caption + "\n\n**[❌ تم رفض الطلب]**", reply_markup=None)

    elif data.startswith("plat_"):
        parts = data.split("_")
        plat = parts[1]
        page = int(parts[2]) if len(parts) > 2 else 0
        
        matched_cats = [c for c in cached_categories if plat in c]
        per_page = 6
        total_pages = (len(matched_cats) + per_page - 1) // per_page
        
        start_idx = page * per_page
        end_idx = start_idx + per_page
        current_cats = matched_cats[start_idx:end_idx]
        
        keyboard = []
        for cat in current_cats:
            short_btn_name = cat.replace("تيك توك", "").replace("فيسبوك", "").replace("انستقرام", "").replace("سناب شات", "").strip()
            if not short_btn_name:
                short_btn_name = cat
            keyboard.append([InlineKeyboardButton(f"📂 {short_btn_name}", callback_data=f"cat_{cat[:20]}")])
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"plat_{plat}_{page-1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"plat_{plat}_{page+1}"))
        if nav_buttons:
            keyboard.append(nav_buttons)
            
        keyboard.append([InlineKeyboardButton("🔙 رجوع للمنصات", callback_data="show_categories")])
        
        page_info = f" (صفحة {page+1} من {total_pages})" if total_pages > 1 else ""
        await query.edit_message_text(f"📋 **أقسام {plat}{page_info}:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("cat_"):
        short = data.replace("cat_", "")
        cat_name = next((c for c in cached_categories if c[:20] == short), None)
        if cat_name:
            keyboard = []
            for i, s in enumerate(cached_categories[cat_name][:10], 1):
                btn_label = f"{i}. {s['name']}"
                if len(btn_label) > 35:
                    btn_label = btn_label[:32] + "..."
                keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"srv_{s.get('service')}")] )
        else:
            keyboard = []
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="show_categories")])
        
        desc_text = f"📂 **قسم: {cat_name}**\n\n👇 **اختر الخدمة المناسبة من الأزرار أدناه:**\n"
        if cat_name and cached_categories[cat_name]:
            for i, s in enumerate(cached_categories[cat_name][:10], 1):
                desc_text += f"\n`{i}.` {s['name']}"
                
        await query.edit_message_text(desc_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("srv_"):
        srv_id = data.replace("srv_", "")
        found_service = None
        for cat in cached_categories:
            for s in cached_categories[cat]:
                if str(s.get('service')) == srv_id:
                    found_service = s
                    break
            if found_service:
                break
        
        if found_ser: