# ⚡ BÁO CÁO TỔNG HỢP HỆ THỐNG BOT QUẢN LÝ CÔNG VIỆC & DAILY CHECKLIST

> **Ngày hoàn thành:** 10/10/2026  
> **Dự án:** Bot Quản lý công việc, Nhắc nhở thông minh 24/7 & Đồng bộ Google Sheets / Excel  
> **Trạng thái:** ✅ Đã hoàn thành 100% & Đang hoạt động Live 24/7 trên Render Cloud.

---

## 📌 1. TỔNG QUAN HỆ THỐNG

Hệ thống được thiết kế để giải quyết triệt để vấn đề quên việc, không quản lý được các đầu công việc hàng ngày, hỗ trợ nhắc nhở đúng giờ và tự động lưu vết nhật ký hoàn thành.

### Các thành phần chính:
1. **Telegram Bot (`QUANTASK_bot`)**:
   - Gửi tin nhắn thông báo **2 lần / công việc** (Lần 1: Trước 15 phút, Lần 2: Đúng giờ hẹn).
   - Đầy đủ nút bấm tương tác: `[✅ Hoàn thành]`, `[⏰ Nhắc lại 15p]`, `[❌ Hủy bỏ]`.
   - Hỗ trợ xem **`📆 Checklist hôm nay`**, **`📝 Ghi chú việc đã làm`**, **`🔍 Tìm kiếm`**, **`📊 Tải file Excel`**.
2. **Đồng Bộ Tự Động Google Sheets**:
   - Sử dụng **Google Apps Script Web App** để đồng bộ 3 Tab dữ liệu sang trang tính Google trực tuyến ngay lập tức khi có thay đổi.
3. **Cơ Sở Dữ Liệu SQLite & Backup Excel**:
   - File Excel `Quan_Ly_Cong_Viec.xlsx` bắt đầu gọn gàng từ **Dòng 1** (Row 1).
   - Cơ sở dữ liệu SQLite tự động nạp lại 18 công việc lặp lại khi khởi tạo trên Cloud.
4. **Máy Chủ Cloud 24/7 (Render.com)**:
   - Chạy trên gói Web Service Free Tier với tích hợp **Flask Health Check Server** giúp Bot thức 24/7/365 kể cả khi tắt máy tính.

---

## 📋 2. DANH SÁCH 18 CÔNG VIỆC HÀNG NGÀY ĐÃ THIẾT LẬP

| STT | Giờ nhắc | Tên công việc | Loại việc | Phân loại |
| :---: | :---: | :--- | :---: | :---: |
| 1 | `08:30` | Đăng video kênh TikTok nam | 🔄 Hàng ngày | `#TikTok` |
| 2 | `08:30` | Đăng video kênh TikTok nữ | 🔄 Hàng ngày | `#TikTok` |
| 3 | `08:30` | Check kênh TikTok Ốp | 🔄 Hàng ngày | `#TikTok` |
| 4 | `09:30` | Đăng video kênh TikTok Tạp hóa | 🔄 Hàng ngày | `#TikTok` |
| 5 | `10:00` | Đăng Video/bài Page Hoang Anh | 🔄 Hàng ngày | `#Fanpage` |
| 6 | `10:00` | Đăng Video/bài Page TunsT | 🔄 Hàng ngày | `#Fanpage` |
| 7 | `10:00` | Đăng Video/bài Page TunsT3k2 | 🔄 Hàng ngày | `#Fanpage` |
| 8 | `10:00` | Đăng Video/bài FaceBook TunsT Tran | 🔄 Hàng ngày | `#Facebook` |
| 9 | `11:00` | Đăng video Shopee | 🔄 Hàng ngày | `#Shopee` |
| 10 | `20:00` | Đăng video kênh TikTok nam | 🔄 Hàng ngày | `#TikTok` |
| 11 | `20:00` | Đăng video kênh TikTok nữ | 🔄 Hàng ngày | `#TikTok` |
| 12 | `20:00` | Đăng video kênh TikTok Tạp hóa | 🔄 Hàng ngày | `#TikTok` |
| 13 | `20:00` | Đăng Video/bài Page Hoang Anh | 🔄 Hàng ngày | `#Fanpage` |
| 14 | `20:00` | Đăng Video/bài Page TunsT | 🔄 Hàng ngày | `#Fanpage` |
| 15 | `20:00` | Đăng Video/bài Page TunsT3k2 | 🔄 Hàng ngày | `#Fanpage` |
| 16 | `20:00` | Đăng Video/bài FaceBook TunsT Tran | 🔄 Hàng ngày | `#Facebook` |
| 17 | `21:00` | Làm video Nam Nữ | 🔄 Hàng ngày | `#Production` |
| 18 | `22:00` | Đăng video Shopee | 🔄 Hàng ngày | `#Shopee` |

---

## 🔔 3. CƠ CHẾ THÔNG BÁO DÚP (2 LẦN)

1. **Lần 1 (Trước 15 phút)**:
   - Gửi tin nhắn cảnh báo chuẩn bị:  
     `⚠️ SẮP ĐẾN HẠN CÔNG VIỆC (Còn 15 phút nữa)!`
2. **Lần 2 (Đúng giờ hẹn)**:
   - Gửi tin nhắn thông báo hành động kèm các nút bấm:  
     `⏰ NHẮC NHỞ ĐÚNG GIỜ CÔNG VIỆC!`  
     `[✅ Hoàn thành]` `[⏰ Nhắc lại 15 phút]` `[❌ Hủy bỏ]`

---

## 📂 4. DANH SÁCH MÃ NGUỒN CỦA DỰ ÁN

- [bot.py](bot.py): Script Telegram Bot chính + Flask Health Check Server.
- [database.py](database.py): SQLite helper + Tự động nạp 18 công việc hàng ngày.
- [google_sheets_sync.py](google_sheets_sync.py): Mô-đun gửi dữ liệu sang Google Sheets.
- [google_apps_script.js](google_apps_script.js): Mã Apps Script nhận dữ liệu bên Google Sheets.
- [excel_exporter.py](excel_exporter.py): Xuất file Excel `Quan_Ly_Cong_Viec.xlsx` bắt đầu từ Dòng 1.
- [scheduler.py](scheduler.py): Bộ hẹn giờ gửi thông báo 2 lần.
- [web_dashboard.py](web_dashboard.py): Giao diện Web quản lý bằng trình duyệt.
- [.env](.env): Lưu cấu hình `BOT_TOKEN`, `GOOGLE_SCRIPT_URL`, `TIMEZONE`.
- [Procfile](Procfile): Cấu hình Web Service cho Render.com.
- [render.yaml](render.yaml): Blueprint cấu hình tự động Web Service trên Render.com.
- [requirements.txt](requirements.txt): Thư viện Python phụ thuộc (đã bổ sung `requests` và `gunicorn`).
- [Quan_Ly_Cong_Viec.xlsx](Quan_Ly_Cong_Viec.xlsx): File Excel tổng hợp.

---

## 🛠️ 5. CÁC NGUYÊN NHÂN RENDER BÁO LỖI & ĐÃ ĐƯỢC XỬ LÝ (FIXED)

1. **Thiếu thư viện `requests` trong `requirements.txt`**:
   - *Sự cố:* `google_sheets_sync.py` gọi `import requests` nhưng `requirements.txt` thiếu `requests`, dẫn đến crash `ModuleNotFoundError` khi Render khởi chạy.
   - *Khắc phục:* Đã bổ sung `requests>=2.31.0` và `gunicorn>=21.2.0` vào `requirements.txt`.

2. **Cấu hình sai loại Service trên Render (`type: worker` vs `type: web`)**:
   - *Sự cố:* `render.yaml` và `Procfile` cấu hình kiểu `worker`. Trên gói Render Free Tier, service dạng **Worker** bị tính phí/từ chối triển khai và không mở cổng HTTP `$PORT`.
   - *Khắc phục:* Đã chuyển `Procfile` thành `web: python bot.py` và `render.yaml` thành `type: web` với `healthCheckPath: /`.

3. **Cơ chế Health Check Server**:
   - `bot.py` tích hợp sẵn máy chủ Flask lắng nghe trên `$PORT` (cổng Render cấp tự động), trả về HTTP status `200 OK` để duy trì Bot hoạt động 24/7.

---

## 📖 6. HƯỚNG DẪN CÂU LỆNH TELEGRAM NHANH

- `/checklist` hoặc bấm nút **`📆 Checklist hôm nay`**: Xem checklist công việc hôm nay.
- `/nhac <Thời gian> <Tên việc>`: Thêm việc mới (Ví dụ: `/nhac 16:00 Duyệt kịch bản #Marketing`).
- `/nhac_hang_ngay <Giờ> <Tên việc>`: Thêm việc lặp lại mỗi ngày.
- `/dalam <Nội dung>`: Lưu nhật ký công việc vừa hoàn thành.
- `/tim <Từ khóa>`: Tìm kiếm lại công việc / nhật ký.
- `/excel`: Tải file Excel quản lý trực tiếp về Telegram.

