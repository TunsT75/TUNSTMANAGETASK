import os
import re
import datetime
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from pytz import timezone

from config import BOT_TOKEN, TIMEZONE, EXCEL_PATH
from database import (
    add_task, log_work, mark_task_completed, update_task_status, 
    delete_task, get_pending_tasks, get_today_work_logs, get_daily_checklist,
    search_tasks_and_logs, get_now
)
from excel_exporter import export_to_excel, sync_all_exports
from scheduler import start_scheduler

token_to_use = BOT_TOKEN if (BOT_TOKEN and ":" in BOT_TOKEN and BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN_HERE") else "123456789:AAEFakeTokenForImportTestingOnly"
bot = telebot.TeleBot(token_to_use)

user_states = {}

def build_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📆 Checklist hôm nay"),
        KeyboardButton("➕ Thêm việc mới"),
        KeyboardButton("📝 Ghi chú việc đã làm"),
        KeyboardButton("📋 Danh sách việc cần làm"),
        KeyboardButton("✅ Việc đã xong hôm nay"),
        KeyboardButton("🔍 Tìm kiếm công việc"),
        KeyboardButton("📊 Tải file Excel quản lý"),
        KeyboardButton("❓ Hướng dẫn nâng cao")
    )
    return markup

def parse_smart_due_time(input_str):
    now = get_now()
    text = input_str.strip().lower()

    m_match = re.match(r"^(\d+)\s*m$", text)
    if m_match:
        minutes = int(m_match.group(1))
        return (now + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:00")

    h_match = re.match(r"^(\d+)\s*h$", text)
    if h_match:
        hours = int(h_match.group(1))
        return (now + datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:00")

    mai_match = re.match(r"^(?:mai|ngày mai)\s+(\d{1,2}:\d{2})$", text)
    if mai_match:
        time_part = mai_match.group(1)
        tomorrow = now + datetime.timedelta(days=1)
        return f"{tomorrow.strftime('%Y-%m-%d')} {time_part}:00"

    if re.match(r"^\d{1,2}:\d{2}$", text):
        return f"{now.strftime('%Y-%m-%d')} {text}:00"

    if re.match(r"^\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}$", text):
        return f"{text}:00"

    return (now + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:00")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 *Chào bạn! Tôi là Bot Quản Lý, Nhắc Nhở & Checklist Công Việc Pro.*\n\n"
        "Tôi giúp bạn **quản lý checklist hàng ngày**, **nhắc nhở chuẩn giờ 24/7**, **ghi nhật ký đã làm** và **tự động đồng bộ Excel & Google Sheets**!\n\n"
        "⚡ *CHECKLIST HÀNG NGÀY:*\n"
        "• `/checklist` - Xem checklist công việc cố định + phát sinh hôm nay\n"
        "• `/nhac_hang_ngay 08:30 Điểm danh sáng` - Tạo việc cố định lặp lại mỗi ngày\n\n"
        "⚡ *TẠO NHẮC VIỆC & NHẬT KÝ SIÊU TỐC:*\n"
        "• `/nhac 15:30 Họp khách hàng` - Nhắc việc lúc 15:30 hôm nay\n"
        "• `/nhac 30m Kiểm tra kho` - Nhắc sau 30 phút nữa\n"
        "• `/dalam #Marketing Đã xong banner ME` - Ghi nhận việc vừa làm xong\n"
        "• `/tim kịch bản` - Tìm kiếm lại công việc hoặc nhật ký\n"
        "• `/excel` - Tải file Excel quản lý tức thì\n\n"
        "Sử dụng Menu bên dưới để thao tác dễ dàng 👇"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=build_main_keyboard())

# -------------------------------------------------------------
# SHORTCUT COMMAND HANDLERS
# -------------------------------------------------------------
@bot.message_handler(commands=['checklist'])
def handle_checklist_command(message):
    today_str = get_now().strftime("%d/%m/%Y")
    daily_tasks = get_daily_checklist(user_id=message.chat.id)

    if not daily_tasks:
        bot.send_message(message.chat.id, f"🎉 *Checklist hôm nay ({today_str}) chưa có công việc nào!*", parse_mode="Markdown")
        return

    msg_text = f"📆 *CHECKLIST CÔNG VIỆC HÔM NAY ({today_str}):*\n\n"
    markup = InlineKeyboardMarkup()

    for t in daily_tasks:
        # t: id, title, category, priority, status, due_time, repeat_type, completed_at
        t_id, title, category, priority, status, due_time, repeat_type, completed_at = t
        chk = "☑️" if status == "Hoàn thành" else "☐"
        type_str = " 🔄 (Hàng ngày)" if repeat_type == "daily" else ""
        time_display = due_time if due_time else "Cả ngày"

        msg_text += f"{chk} `[#{t_id}]` *{title}*{type_str}\n   🏷️ #{category} | 🕒 {time_display}\n\n"

        if status != "Hoàn thành":
            markup.add(
                InlineKeyboardButton(f"☑ Tick xong #{t_id}", callback_data=f"done_{t_id}"),
                InlineKeyboardButton(f"⏰ Hoãn 15p", callback_data=f"snooze_{t_id}")
            )

    bot.send_message(message.chat.id, msg_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['nhac'])
def handle_quick_reminder(message):
    text = message.text.replace("/nhac", "").strip()
    if not text:
        bot.reply_to(message, "⚠️ Cú pháp: `/nhac <Thời gian> <Tên công việc>`\nVí dụ:\n• `/nhac 15:30 Họp sản phẩm`\n• `/nhac 30m Gọi điện cho sếp`\n• `/nhac mai 09:00 Gửi hợp đồng`", parse_mode="Markdown")
        return

    parts = text.split(" ", 1)
    time_part = parts[0]
    title = parts[1] if len(parts) > 1 else text

    due_time_str = parse_smart_due_time(time_part)

    category = "Chung"
    cat_match = re.search(r"#(\w+)", title)
    if cat_match:
        category = cat_match.group(1)
        title = title.replace(f"#{category}", "").strip()

    task_id = add_task(title=title, category=category, due_time=due_time_str, user_id=message.chat.id)
    sync_all_exports()

    bot.reply_to(
        message, 
        f"✅ *Đã tạo nhắc nhở thành công!*\n\n"
        f"📌 **Công việc:** {title}\n"
        f"🏷️ **Phân loại:** #{category}\n"
        f"⏰ **Thời gian nhắc:** {due_time_str}\n\n"
        f"📊 *Đã đồng bộ tự động vào Excel & Google Sheets!*",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['nhac_hang_ngay'])
def handle_daily_recurring(message):
    text = message.text.replace("/nhac_hang_ngay", "").strip()
    if not text:
        bot.reply_to(message, "⚠️ Cú pháp: `/nhac_hang_ngay <Giờ HH:MM> <Tên việc lặp lại>`\nVí dụ: `/nhac_hang_ngay 09:00 Gửi báo cáo doanh thu`", parse_mode="Markdown")
        return

    parts = text.split(" ", 1)
    time_part = parts[0]
    title = parts[1] if len(parts) > 1 else text

    due_time_str = parse_smart_due_time(time_part)

    category = "Chung"
    cat_match = re.search(r"#(\w+)", title)
    if cat_match:
        category = cat_match.group(1)
        title = title.replace(f"#{category}", "").strip()

    task_id = add_task(title=title, category=category, due_time=due_time_str, user_id=message.chat.id, repeat_type="daily")
    sync_all_exports()

    bot.reply_to(
        message, 
        f"🔄 *Đã thêm việc LẶP LẠI HÀNG NGÀY vào Checklist!*\n\n"
        f"📌 **Công việc:** {title}\n"
        f"🏷️ **Phân loại:** #{category}\n"
        f"⏰ **Giờ nhắc mỗi ngày:** {time_part}\n"
        f"📊 *Đã xuất ra Checklist Excel & Google Sheets!*",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['dalam', 'note'])
def handle_quick_log(message):
    content = message.text.replace("/dalam", "").replace("/note", "").strip()
    if not content:
        bot.reply_to(message, "⚠️ Cú pháp: `/dalam <Nội dung việc đã làm>`\nVí dụ: `/dalam #Design Đã xong banner campaign`", parse_mode="Markdown")
        return

    category = "Chung"
    cat_match = re.search(r"#(\w+)", content)
    if cat_match:
        category = cat_match.group(1)
        content = content.replace(f"#{category}", "").strip()

    log_id = log_work(content=content, category=category, user_id=message.chat.id)
    sync_all_exports()

    now_time = get_now().strftime("%H:%M:%S")
    bot.reply_to(
        message,
        f"📝 *Đã ghi nhận công việc hoàn thành!*\n\n"
        f"🏷️ **Phân loại:** #{category}\n"
        f"🕒 **Thời gian:** {now_time}\n"
        f"🎯 **Nội dung:** {content}\n\n"
        f"📊 *Đã cập nhật vào Nhật ký Excel & Google Sheets!*",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['tim', 'search'])
def handle_search(message):
    keyword = message.text.replace("/tim", "").replace("/search", "").strip()
    if not keyword:
        bot.reply_to(message, "⚠️ Cú pháp tìm kiếm: `/tim <từ khóa>`\nVí dụ: `/tim kịch bản`", parse_mode="Markdown")
        return

    tasks, logs = search_tasks_and_logs(keyword, user_id=message.chat.id)
    
    msg_text = f"🔍 *KẾT QUẢ TÌM KIẾM CHO TỪ KHÓA:* `{keyword}`\n\n"

    if tasks:
        msg_text += f"📋 **Công việc liên quan ({len(tasks)}):**\n"
        for t in tasks:
            msg_text += f"• `[#{t[0]}]` [{t[4]}] *{t[1]}* ({t[2]}) - Hạn: {t[3] or 'Không'}\n"
        msg_text += "\n"

    if logs:
        msg_text += f"📝 **Nhật ký đã làm ({len(logs)}):**\n"
        for l in logs:
            msg_text += f"• `[{l[2]} {l[3]}]` #{l[4]}: {l[1]}\n"

    if not tasks and not logs:
        msg_text += "❌ *Không tìm thấy kết quả nào phù hợp.*"

    bot.reply_to(message, msg_text, parse_mode="Markdown")

@bot.message_handler(commands=['excel'])
def send_excel_file(message):
    sync_all_exports()
    if os.path.exists(EXCEL_PATH):
        with open(EXCEL_PATH, 'rb') as f:
            bot.send_document(
                message.chat.id, 
                f, 
                caption="📊 *File Quản Lý Công Việc & Daily Checklist Mới Nhất*", 
                parse_mode="Markdown"
            )
    else:
        bot.reply_to(message, "⚠️ Không tìm thấy file Excel.")

# -------------------------------------------------------------
# BUTTON HANDLERS
# -------------------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text == "📆 Checklist hôm nay")
def handle_checklist_btn(message):
    handle_checklist_command(message)

@bot.message_handler(func=lambda msg: msg.text == "📊 Tải file Excel quản lý")
def handle_excel_btn(message):
    send_excel_file(message)

@bot.message_handler(func=lambda msg: msg.text == "📋 Danh sách việc cần làm")
def handle_list_pending(message):
    tasks = get_pending_tasks(user_id=message.chat.id)
    if not tasks:
        bot.send_message(message.chat.id, "🎉 *Tuyệt vời! Bạn không có công việc nào đang tồn đọng.*", parse_mode="Markdown")
        return

    msg_text = f"📋 *DANH SÁCH CÔNG VIỆC CẦN LÀM ({len(tasks)} việc):*\n\n"
    markup = InlineKeyboardMarkup()

    for task in tasks:
        t_id, title, desc, category, priority, due_time, created_at, repeat_type = task
        p_emoji = "🔴" if priority == "Cao" else ("🟡" if priority == "Trung bình" else "🔵")
        due_display = due_time if due_time else "Chưa đặt lịch"
        repeat_display = " 🔄 (Hàng ngày)" if repeat_type == "daily" else ""

        msg_text += f"🔹 `[#{t_id}]` {p_emoji} *{title}*{repeat_display}\n   🏷️ #{category} | 🕒 Hạn: {due_display}\n"
        if desc:
            msg_text += f"   📝 {desc}\n"
        msg_text += "\n"

        markup.add(
            InlineKeyboardButton(f"✅ Xong #{t_id}", callback_data=f"done_{t_id}"),
            InlineKeyboardButton(f"❌ Xóa #{t_id}", callback_data=f"delete_{t_id}")
        )

    bot.send_message(message.chat.id, msg_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "✅ Việc đã xong hôm nay")
def handle_today_summary(message):
    logs = get_today_work_logs(user_id=message.chat.id)
    today_str = get_now().strftime("%d/%m/%Y")

    if not logs:
        bot.send_message(message.chat.id, f"📝 *Hôm nay ({today_str}) bạn chưa ghi nhận công việc nào đã hoàn thành.*\nHãy gõ `/dalam <nội dung>` để ghi nhận nhé!", parse_mode="Markdown")
        return

    msg_text = f"✅ *TỔNG KẾT CÔNG VIỆC HOÀN THÀNH HÔM NAY ({today_str}):*\n\n"
    for idx, log in enumerate(logs, 1):
        msg_text += f"{idx}. `[{log[2]}]` #{log[3]}: *{log[1]}*\n"

    msg_text += f"\n📊 *Tổng cộng:* {len(logs)} công việc đã hoàn tất!"
    bot.send_message(message.chat.id, msg_text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "🔍 Tìm kiếm công việc")
def prompt_search(message):
    user_states[message.chat.id] = {"step": "WAITING_SEARCH_KW"}
    bot.send_message(message.chat.id, "🔍 *Hãy nhập từ khóa bạn muốn tìm kiếm:*", parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "❓ Hướng dẫn nâng cao")
def handle_guide(message):
    send_welcome(message)

# -------------------------------------------------------------
# WIZARDS & STEP-BY-STEP HANDLERS
# -------------------------------------------------------------
@bot.message_handler(func=lambda msg: msg.text == "➕ Thêm việc mới")
def start_add_task_wizard(message):
    user_states[message.chat.id] = {"step": "WAITING_TITLE"}
    bot.send_message(
        message.chat.id, 
        "✏️ *Hãy nhập tên công việc cần làm:*\n(Ví dụ: *Gửi báo cáo doanh số #Marketing*)",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda msg: msg.text == "📝 Ghi chú việc đã làm")
def start_log_work_wizard(message):
    user_states[message.chat.id] = {"step": "WAITING_LOG_CONTENT"}
    bot.send_message(
        message.chat.id, 
        "📝 *Hãy nhập chi tiết công việc bạn vừa làm xong:*\n(Ví dụ: *Đã hoàn thiện thiết kế banner ME #Design*)",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda msg: msg.chat.id in user_states)
def handle_wizard_steps(message):
    state = user_states.get(message.chat.id)
    if not state:
        return

    step = state.get("step")

    if step == "WAITING_SEARCH_KW":
        user_states.pop(message.chat.id, None)
        message.text = f"/tim {message.text}"
        handle_search(message)

    elif step == "WAITING_TITLE":
        text = message.text
        category = "Chung"
        cat_match = re.search(r"#(\w+)", text)
        if cat_match:
            category = cat_match.group(1)
            text = text.replace(f"#{category}", "").strip()

        state["title"] = text
        state["category"] = category
        state["step"] = "WAITING_PRIORITY"
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🔴 Cao", callback_data="prio_Cao"),
            InlineKeyboardButton("🟡 Trung bình", callback_data="prio_Trung bình"),
            InlineKeyboardButton("🔵 Thấp", callback_data="prio_Thấp")
        )
        bot.send_message(message.chat.id, "🎯 *Chọn mức độ ưu tiên của công việc:*", parse_mode="Markdown", reply_markup=markup)

    elif step == "WAITING_DUE_TIME":
        text = message.text.strip()
        due_time_str = parse_smart_due_time(text)

        task_id = add_task(
            title=state["title"],
            category=state.get("category", "Chung"),
            priority=state.get("priority", "Trung bình"),
            due_time=due_time_str,
            user_id=message.chat.id
        )
        sync_all_exports()
        user_states.pop(message.chat.id, None)

        bot.send_message(
            message.chat.id,
            f"🎉 *Đã thêm công việc thành công!*\n\n"
            f"📌 **Tên việc:** {state['title']}\n"
            f"🏷️ **Phân loại:** #{state.get('category', 'Chung')}\n"
            f"🎯 **Ưu tiên:** {state.get('priority', 'Trung bình')}\n"
            f"⏰ **Giờ nhắc:** {due_time_str}\n\n"
            f"📊 *Đã đồng bộ tự động vào Excel & Google Sheets!*",
            parse_mode="Markdown",
            reply_markup=build_main_keyboard()
        )

    elif step == "WAITING_LOG_CONTENT":
        text = message.text
        category = "Chung"
        cat_match = re.search(r"#(\w+)", text)
        if cat_match:
            category = cat_match.group(1)
            text = text.replace(f"#{category}", "").strip()

        log_work(content=text, category=category, user_id=message.chat.id)
        sync_all_exports()
        user_states.pop(message.chat.id, None)

        bot.send_message(
            message.chat.id,
            f"✅ *Đã lưu nhật ký công việc đã làm!*\n\n"
            f"🏷️ **Phân loại:** #{category}\n"
            f"🎯 **Nội dung:** {text}\n"
            f"📊 *Đã ghi nhận vào Nhật ký Excel & Google Sheets.*",
            parse_mode="Markdown",
            reply_markup=build_main_keyboard()
        )

# -------------------------------------------------------------
# INLINE CALLBACK HANDLER
# -------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    data = call.data
    chat_id = call.message.chat.id

    if data.startswith("prio_"):
        prio = data.replace("prio_", "")
        if chat_id in user_states:
            user_states[chat_id]["priority"] = prio
            user_states[chat_id]["step"] = "WAITING_DUE_TIME"
            bot.edit_message_text(
                f"✅ Đã chọn độ ưu tiên: *{prio}*\n\n⏰ *Hãy nhập thời gian nhắc nhở (Ví dụ: `16:30` hoặc `30m` hoặc `mai 09:00` hoặc `2026-10-15 09:00`):*",
                chat_id, call.message.message_id, parse_mode="Markdown"
            )

    elif data.startswith("done_"):
        t_id = int(data.replace("done_", ""))
        mark_task_completed(t_id, auto_log=True, user_id=chat_id)
        sync_all_exports()
        bot.answer_callback_query(call.id, "🎉 Đã đánh dấu hoàn thành & lưu nhật ký!")
        bot.edit_message_text(f"✅ *Đã hoàn thành công việc #{t_id}!*", chat_id, call.message.message_id, parse_mode="Markdown")

    elif data.startswith("snooze_"):
        t_id = int(data.replace("snooze_", ""))
        now = get_now()
        new_due = (now + datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:00")
        
        sqlite3_update_due(t_id, new_due)
        sync_all_exports()
        bot.answer_callback_query(call.id, "⏰ Đã dời lịch nhắc thêm 15 phút!")
        bot.edit_message_text(f"⏰ *Đã dời lịch nhắc công việc #{t_id} thêm 15 phút (Lúc {new_due}).*", chat_id, call.message.message_id, parse_mode="Markdown")

    elif data.startswith("cancel_"):
        t_id = int(data.replace("cancel_", ""))
        update_task_status(t_id, "Đã hủy")
        sync_all_exports()
        bot.answer_callback_query(call.id, "❌ Đã hủy công việc!")
        bot.edit_message_text(f"❌ *Đã hủy bỏ công việc #{t_id}.*", chat_id, call.message.message_id, parse_mode="Markdown")

    elif data.startswith("delete_"):
        t_id = int(data.replace("delete_", ""))
        delete_task(t_id)
        sync_all_exports()
        bot.answer_callback_query(call.id, "🗑️ Đã xóa công việc!")
        bot.edit_message_text(f"🗑️ *Đã xóa công việc #{t_id} khỏi hệ thống.*", chat_id, call.message.message_id, parse_mode="Markdown")

def sqlite3_update_due(task_id, new_due_time):
    import sqlite3
    from config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET due_time = ?, status = 'Chờ làm' WHERE id = ?", (new_due_time, task_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Starting Task Reminder Bot Pro with Daily Checklist...")
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("⚠️ Warning: Please set BOT_TOKEN in .env file before running!")
    else:
        # Set Bot Command Menu in Telegram UI
        try:
            bot.set_my_commands([
                telebot.types.BotCommand("checklist", "📆 Checklist hôm nay"),
                telebot.types.BotCommand("nhac", "⏰ Nhắc việc (VD: /nhac 15:30 Họp)"),
                telebot.types.BotCommand("nhac_hang_ngay", "🔄 Nhắc lặp lại mỗi ngày"),
                telebot.types.BotCommand("dalam", "📝 Ghi nhật ký việc vừa làm xong"),
                telebot.types.BotCommand("tim", "🔍 Tìm kiếm công việc / nhật ký"),
                telebot.types.BotCommand("excel", "📊 Tải file Excel quản lý"),
                telebot.types.BotCommand("help", "❓ Hướng dẫn chi tiết")
            ])
        except Exception as e:
            print(f"Notice setting bot commands: {e}")

        start_scheduler(bot)
        print("Scheduler started. Bot is polling...")
        bot.infinity_polling()

