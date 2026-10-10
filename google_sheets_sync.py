import os
import requests
import gspread
from config import BASE_DIR, TIMEZONE
from database import get_all_tasks, get_all_work_logs, get_daily_checklist, get_now

CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL", "")

def safe_print(msg):
    try:
        print(msg)
    except Exception:
        print(msg.encode('ascii', 'ignore').decode('ascii'))

def sync_to_google_sheets():
    """Tự động đồng bộ toàn bộ công việc & nhật ký lên Google Sheets"""
    
    tasks = get_all_tasks()
    logs = get_all_work_logs()
    daily_checklist = get_daily_checklist()
    
    # -------------------------------------------------------------
    # PHƯƠNG PHÁP 1: SỬ DỤNG GOOGLE APPS SCRIPT WEB APP (CỰC KỲ ĐƠN GIẢN!)
    # -------------------------------------------------------------
    if GOOGLE_SCRIPT_URL and GOOGLE_SCRIPT_URL != "YOUR_GOOGLE_SCRIPT_URL_HERE":
        try:
            # 0. Daily checklist rows
            headers0 = ["STT", "Checkbox", "Tên công việc", "Loại việc", "Phân loại", "Độ ưu tiên", "Hạn chót / Giờ nhắc", "Trạng thái", "Giờ hoàn thành"]
            daily_rows = [headers0]
            for idx, t in enumerate(daily_checklist, 1):
                chk = "☑" if t[4] == "Hoàn thành" else "☐"
                type_str = "🔄 Lặp lại hàng ngày" if t[6] == "daily" else "📌 Việc phát sinh"
                daily_rows.append([idx, chk, t[1], type_str, t[2] or "Chung", t[3], t[5] or "", t[4], t[7] or ""])

            # 1. All tasks rows
            headers1 = ["Mã ID", "Tên công việc", "Ghi chú / Chi tiết", "Phân loại", "Độ ưu tiên", "Trạng thái", "Hạn chót / Giờ nhắc", "Lặp lại", "Ngày tạo", "Ngày hoàn thành"]
            task_rows = [headers1]
            for t in tasks:
                task_rows.append([
                    t[0], t[1], t[2] or "", t[3] or "Chung", t[4], t[5], t[6] or "",
                    "Hàng ngày" if t[9] == "daily" else "Không", t[7] or "", t[8] or ""
                ])

            # 2. Logs rows
            headers2 = ["STT", "Mã Task Ref", "Phân loại", "Ngày thực hiện", "Thời gian", "Nội dung công việc đã làm"]
            log_rows = [headers2]
            for idx, l in enumerate(logs, 1):
                log_rows.append([idx, l[1] if l[1] else "-", l[2] or "Chung", l[4], l[5], l[3]])

            payload = {
                "daily": daily_rows,
                "tasks": task_rows,
                "logs": log_rows,
                "updated_at": get_now().strftime("%d/%m/%Y %H:%M:%S")
            }

            res = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
            if res.status_code == 200:
                safe_print("Google Sheets (Apps Script): Synchronized successfully 100%!")
                return True
            else:
                safe_print(f"Google Apps Script returned status: {res.status_code}")
        except Exception as e:
            safe_print(f"Error syncing via Apps Script Web App: {e}")

    # -------------------------------------------------------------
    # PHƯƠNG PHÁP 2: SỬ DỤNG CREDENTIALS.JSON (GSPREAD)
    # -------------------------------------------------------------
    if os.path.exists(CREDENTIALS_PATH) and GOOGLE_SHEET_ID and GOOGLE_SHEET_ID != "YOUR_GOOGLE_SHEET_ID_HERE":
        try:
            gc = gspread.service_account(filename=CREDENTIALS_PATH)
            sh = gc.open_by_key(GOOGLE_SHEET_ID)

            # Daily checklist sheet
            try:
                ws0 = sh.worksheet("📆 Checklist hôm nay")
            except gspread.WorksheetNotFound:
                ws0 = sh.add_worksheet(title="📆 Checklist hôm nay", rows=200, cols=10)
            ws0.clear()
            headers0 = ["STT", "Checkbox", "Tên công việc", "Loại việc", "Phân loại", "Độ ưu tiên", "Hạn chót / Giờ nhắc", "Trạng thái", "Giờ hoàn thành"]
            daily_rows = [headers0]
            for idx, t in enumerate(daily_checklist, 1):
                chk = "☑" if t[4] == "Hoàn thành" else "☐"
                type_str = "🔄 Lặp lại hàng ngày" if t[6] == "daily" else "📌 Việc phát sinh"
                daily_rows.append([idx, chk, t[1], type_str, t[2] or "Chung", t[3], t[5] or "", t[4], t[7] or ""])
            ws0.update(values=daily_rows, range_name="A1")

            # All tasks sheet
            try:
                ws1 = sh.worksheet("📋 Tất cả công việc")
            except gspread.WorksheetNotFound:
                ws1 = sh.add_worksheet(title="📋 Tất cả công việc", rows=500, cols=15)
            ws1.clear()
            headers1 = ["Mã ID", "Tên công việc", "Ghi chú / Chi tiết", "Phân loại", "Độ ưu tiên", "Trạng thái", "Hạn chót / Giờ nhắc", "Lặp lại", "Ngày tạo", "Ngày hoàn thành"]
            rows1 = [headers1]
            for task in tasks:
                rows1.append([
                    task[0], task[1], task[2] or "", task[3] or "Chung", task[4], task[5],
                    task[6] or "", "Hàng ngày" if task[9] == "daily" else "Không", task[7] or "", task[8] or ""
                ])
            ws1.update(values=rows1, range_name="A1")

            # Log sheet
            try:
                ws2 = sh.worksheet("📝 Nhật ký đã làm")
            except gspread.WorksheetNotFound:
                ws2 = sh.add_worksheet(title="📝 Nhật ký đã làm", rows=500, cols=10)
            ws2.clear()
            headers2 = ["STT", "Mã Task Ref", "Phân loại", "Ngày thực hiện", "Thời gian", "Nội dung công việc đã làm"]
            rows2 = [headers2]
            for idx, log in enumerate(logs, 1):
                rows2.append([idx, log[1] if log[1] else "-", log[2] or "Chung", log[4], log[5], log[3]])
            ws2.update(values=rows2, range_name="A1")

            safe_print("Google Sheets (Service Account): Synchronized successfully!")
            return True
        except Exception as e:
            safe_print(f"Error syncing Google Sheets via Credentials: {e}")

    safe_print("Google Sheets: Credentials or Web App URL not configured.")
    return False

if __name__ == "__main__":
    sync_to_google_sheets()
