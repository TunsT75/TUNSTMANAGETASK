# ⚡ HỆ THỐNG BOT QUẢN LÝ, NHẮC NHỞ & GHI CHÚ CÔNG VIỆC TỰ ĐỘNG

> Hướng dẫn toàn diện giúp bạn quản lý 100% công việc, không lo bỏ quên công việc, tự động ghi nhận nhật ký làm việc và xuất file Excel quản lý chuyên nghiệp.

---

## 🚀 TÍNH NĂNG NỔI BẬT

1. **🤖 Telegram Bot Nhắc Nhở Thông Minh (24/7)**:
   - Đặt lịch hẹn giờ nhắc nhở qua câu lệnh nhanh hoặc menu tương tác.
   - Gửi tin nhắn thông báo đúng giờ kèm nút bấm tương tác: `[✅ Hoàn thành]`, `[⏰ Nhắc lại 15p]`, `[❌ Hủy bỏ]`.
2. **📝 Ghi Chép Nhật Ký Công Việc Đã Làm (Work Log)**:
   - Ghi lại các việc đã xong trong ngày (`/dalam Nội dung...`).
   - Tra cứu nhanh "Hôm nay tôi đã làm được những gì?".
3. **📊 Tự Động Cập Nhật File Excel (`Quan_Ly_Cong_Viec.xlsx`)**:
   - Đồng bộ tức thì mọi công việc, trạng thái, thời gian nhắc và nhật ký vào file Excel đẹp mắt.
   - 3 Tab riêng biệt: *Danh sách công việc*, *Nhật ký đã làm*, *Báo cáo thống kê hiệu suất*.
4. **🌐 Giao Diện Web Dashboard Trực Quan**:
   - Truy cập ngay trên trình duyệt máy tính (`http://localhost:5000`) để xem tổng quan, thêm việc và tải file Excel.

---

## 🛠️ HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY (3 BƯỚC)

### Bước 1: Tạo Token Bot Telegram (Miễn phí - 1 phút)
1. Mở ứng dụng Telegram trên điện thoại/máy tính, tìm kiếm **`@BotFather`**.
2. Gõ câu lệnh `/newbot` và bấm **Send**.
3. Đặt **Tên Bot** (ví dụ: `My Task Manager Bot`) và **Username** kết thúc bằng `bot` (ví dụ: `TuanTaskManagerBot`).
4. `@BotFather` sẽ gửi lại cho bạn 1 chuỗi **HTTP API Token** (dạng `123456789:ABCdefGhIJKlmNoPQ...`).

### Bước 2: Dán Token vào file `.env`
Mở file `.env` trong thư mục dự án và dán token của bạn vào:
```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQ...
TIMEZONE=Asia/Ho_Chi_Minh
```

### Bước 3: Chạy ứng dụng

#### Option A: Chạy Bot Telegram & Nhắc Nhở
Mở Terminal / Command Prompt tại thư mục dự án và gõ:
```bash
python bot.py
```
*(Bot sẽ bắt đầu hoạt động và sẵn sàng nhận lệnh từ Telegram)*

#### Option B: Chạy Web Dashboard trên Trình Duyệt
```bash
python web_dashboard.py
```
Mở trình duyệt truy cập: **`http://localhost:5000`**

---

## 📖 HƯỚNG DẪN SỬ DỤNG BOT TELEGRAM

### 1. Các Cú Pháp Lệnh Nhanh (Shortcuts):
- `/nhac 14:30 Họp với khách hàng` -> Nhắc nhở công việc vào 14:30 hôm nay.
- `/nhac 2026-10-15 09:00 Gửi hợp đồng` -> Nhắc nhở vào ngày & giờ cụ thể.
- `/dalam Đã hoàn tất thiết kế banner ME` -> Ghi chép nhật ký việc đã làm xong.
- `/excel` -> Tải file Excel quản lý trực tiếp về Telegram.

### 2. Sử dụng Menu Nút Bấm:
- ➕ **Thêm việc mới**: Nhập tên việc, chọn mức độ ưu tiên (🔴 Cao, 🟡 Trung bình, 🔵 Thấp) và đặt giờ nhắc.
- 📝 **Ghi chú việc đã làm**: Lưu nhanh nội dung công việc vừa hoàn thành.
- 📋 **Danh sách việc cần làm**: Xem danh sách việc tồn đọng kèm nút bấm **Xong** / **Xóa**.
- ✅ **Việc đã xong hôm nay**: Tổng kết danh sách các việc bạn đã làm được trong ngày.
- 📊 **Tải file Excel**: Tải file `Quan_Ly_Cong_Viec.xlsx`.

---

## 📂 CẤU TRÚC THƯ MỤC DỰ ÁN

```text
[TUẤN] ZALOBOT/
├── data/
│   └── tasks.db               # Cơ sở dữ liệu SQLite lưu trữ công việc & nhật ký
├── templates/
│   └── index.html             # Giao diện Web Dashboard HTML/CSS
├── bot.py                     # Script chạy Bot Telegram chính & xử lý tương tác
├── database.py                # Xử lý truy vấn dữ liệu SQLite
├── excel_exporter.py          # Script xuất & định dạng file Excel tự động
├── scheduler.py               # Bộ hẹn giờ gửi thông báo nhắc nhở tự động
├── web_dashboard.py           # Web Server Flask quản lý trên trình duyệt
├── config.py                  # Đọc cấu hình & múi giờ
├── Quan_Ly_Cong_Viec.xlsx     # File Excel quản lý công việc tự động
├── requirements.txt           # Danh sách thư viện Python
├── .env                       # File chứa BOT_TOKEN
└── README.md                  # Tài liệu hướng dẫn sử dụng
```
