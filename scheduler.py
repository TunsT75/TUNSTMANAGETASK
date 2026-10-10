import datetime
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from config import TIMEZONE
from database import get_due_tasks_to_remind, get_tasks_for_pre_reminder_15m, update_task_status
from excel_exporter import sync_all_exports

def check_and_send_reminders(bot):
    try:
        # -------------------------------------------------------------
        # 1. NHẮC NHỞ LẦN 1: TRƯỚC 15 PHÚT
        # -------------------------------------------------------------
        pre_tasks = get_tasks_for_pre_reminder_15m()
        for task in pre_tasks:
            # task: id, title, description, category, priority, due_time, user_id
            t_id, title, desc, category, priority, due_time, user_id = task
            p_emoji = "🔴" if priority == "Cao" else ("🟡" if priority == "Trung bình" else "🔵")

            message_text = (
                f"⚠️ *SẮP ĐẾN HẠN CÔNG VIỆC (Còn 15 phút nữa)!*\n\n"
                f"📌 **Tên việc:** {title}\n"
                f"🏷️ **Phân loại:** #{category}\n"
                f"{p_emoji} **Độ ưu tiên:** {priority}\n"
                f"🕒 **Giờ thực hiện:** {due_time}\n"
                f"\n👉 *Hãy chuẩn bị thực hiện nhé! Bot sẽ nhắc lại lần 2 đúng giờ.*"
            )

            if user_id:
                try:
                    bot.send_message(user_id, message_text, parse_mode="Markdown")
                    update_task_status(t_id, "Nhắc 15p")
                    sync_all_exports()
                except Exception as e:
                    print(f"Error sending pre-reminder to user {user_id}: {e}")

        # -------------------------------------------------------------
        # 2. NHẮC NHỞ LẦN 2: ĐÚNG GIỜ HẸN
        # -------------------------------------------------------------
        due_tasks = get_due_tasks_to_remind()
        for task in due_tasks:
            t_id, title, desc, category, priority, due_time, user_id = task
            p_emoji = "🔴" if priority == "Cao" else ("🟡" if priority == "Trung bình" else "🔵")

            message_text = (
                f"⏰ *NHẮC NHỞ ĐÚNG GIỜ CÔNG VIỆC!*\n\n"
                f"📌 **Tên việc:** {title}\n"
                f"🏷️ **Phân loại:** #{category}\n"
                f"{p_emoji} **Độ ưu tiên:** {priority}\n"
                f"🕒 **Hạn chót/Giờ nhắc:** {due_time}\n"
            )
            if desc:
                message_text += f"📝 **Ghi chú:** {desc}\n"
                
            message_text += "\n👇 *Hãy chọn thao tác bên dưới:* "

            from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("✅ Hoàn thành", callback_data=f"done_{t_id}"),
                InlineKeyboardButton("⏰ Nhắc lại 15p", callback_data=f"snooze_{t_id}")
            )
            markup.row(
                InlineKeyboardButton("❌ Hủy bỏ", callback_data=f"cancel_{t_id}")
            )

            if user_id:
                try:
                    bot.send_message(user_id, message_text, parse_mode="Markdown", reply_markup=markup)
                    update_task_status(t_id, "Đang nhắc")
                    sync_all_exports()
                except Exception as e:
                    print(f"Error sending due reminder to user {user_id}: {e}")
    except Exception as e:
        print(f"Error checking reminders: {e}")

def start_scheduler(bot):
    scheduler = BackgroundScheduler(timezone=timezone(TIMEZONE))
    scheduler.add_job(check_and_send_reminders, 'interval', seconds=30, args=[bot])
    scheduler.start()
    return scheduler
