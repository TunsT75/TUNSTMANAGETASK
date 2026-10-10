import sqlite3
import datetime
from pytz import timezone
from config import DB_PATH, TIMEZONE

def get_now():
    tz = timezone(TIMEZONE)
    return datetime.datetime.now(tz)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table 1: Tasks (Công việc cần làm & Lịch nhắc)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'Chung',
            priority TEXT DEFAULT 'Trung bình',
            status TEXT DEFAULT 'Chờ làm',
            due_time TEXT,
            repeat_type TEXT DEFAULT 'none',
            created_at TEXT NOT NULL,
            completed_at TEXT,
            user_id INTEGER
        )
    ''')

    # Table 2: Work Logs (Nhật ký các việc đã làm)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            category TEXT DEFAULT 'Chung',
            content TEXT NOT NULL,
            log_date TEXT NOT NULL,
            log_time TEXT NOT NULL,
            created_at TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    conn.close()

def add_task(title, description="", category="Chung", priority="Trung bình", due_time=None, user_id=None, repeat_type="none"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = get_now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO tasks (title, description, category, priority, status, due_time, repeat_type, created_at, user_id)
        VALUES (?, ?, ?, ?, 'Chờ làm', ?, ?, ?, ?)
    ''', (title, description, category, priority, due_time, repeat_type, now_str, user_id))
    
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def log_work(content, category="Chung", task_id=None, user_id=None):
    """Ghi chép công việc đã thực hiện"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    log_date = now.strftime("%Y-%m-%d")
    log_time = now.strftime("%H:%M:%S")
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO work_logs (task_id, category, content, log_date, log_time, created_at, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (task_id, category, content, log_date, log_time, created_at, user_id))
    
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def mark_task_completed(task_id, auto_log=True, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = get_now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT title, category, repeat_type, due_time FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    title, category, repeat_type, due_time = row
    cursor.execute('''
        UPDATE tasks 
        SET status = 'Hoàn thành', completed_at = ? 
        WHERE id = ?
    ''', (now_str, task_id))

    if auto_log:
        log_date = now.strftime("%Y-%m-%d")
        log_time = now.strftime("%H:%M:%S")
        cursor.execute('''
            INSERT INTO work_logs (task_id, category, content, log_date, log_time, created_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (task_id, category, f"Đã hoàn thành: {title}", log_date, log_time, now_str, user_id))

    # Recurring daily task logic
    if repeat_type == 'daily' and due_time:
        try:
            dt_obj = datetime.datetime.strptime(due_time, "%Y-%m-%d %H:%M:%S")
            next_due = (dt_obj + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO tasks (title, category, priority, status, due_time, repeat_type, created_at, user_id)
                VALUES (?, ?, 'Trung bình', 'Chờ làm', ?, 'daily', ?, ?)
            ''', (title, category, next_due, now_str, user_id))
        except Exception as e:
            print(f"Error creating next recurring task: {e}")

    conn.commit()
    conn.close()
    return True

def get_daily_checklist(user_id=None, date_str=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if not date_str:
        date_str = get_now().strftime("%Y-%m-%d")
    
    query = '''
        SELECT id, title, category, priority, status, due_time, repeat_type, completed_at
        FROM tasks
        WHERE (due_time LIKE ? OR repeat_type = 'daily' OR (completed_at LIKE ?))
    '''
    params = [f"{date_str}%", f"{date_str}%"]
    if user_id:
        query += " AND (user_id = ? OR user_id IS NULL)"
        params.append(user_id)
    query += " ORDER BY status ASC, due_time ASC, id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_task_status(task_id, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_pending_tasks(user_id=None, category=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT id, title, description, category, priority, due_time, created_at, repeat_type FROM tasks WHERE status != 'Hoàn thành' AND status != 'Đã hủy'"
    params = []
    if user_id:
        query += " AND (user_id = ? OR user_id IS NULL)"
        params.append(user_id)
    if category and category != 'Tất cả':
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY due_time ASC, id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_today_work_logs(user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = get_now().strftime("%Y-%m-%d")
    query = "SELECT id, content, log_time, category FROM work_logs WHERE log_date = ?"
    params = [today_str]
    if user_id:
        query += " AND (user_id = ? OR user_id IS NULL)"
        params.append(user_id)
    query += " ORDER BY log_time ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_tasks_and_logs(keyword, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    kw = f"%{keyword}%"
    
    cursor.execute('''
        SELECT id, title, status, due_time, priority, category FROM tasks
        WHERE (title LIKE ? OR description LIKE ? OR category LIKE ?)
        ORDER BY id DESC LIMIT 15
    ''', (kw, kw, kw))
    tasks = cursor.fetchall()

    cursor.execute('''
        SELECT id, content, log_date, log_time, category FROM work_logs
        WHERE (content LIKE ? OR category LIKE ?)
        ORDER BY id DESC LIMIT 15
    ''', (kw, kw))
    logs = cursor.fetchall()

    conn.close()
    return tasks, logs

def get_all_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, category, priority, status, due_time, created_at, completed_at, repeat_type FROM tasks ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_work_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_id, category, content, log_date, log_time, created_at FROM work_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_due_tasks_to_remind():
    """Lấy các công việc ĐÚNG GIỜ để nhắc nhở lần 2"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = get_now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        SELECT id, title, description, category, priority, due_time, user_id 
        FROM tasks 
        WHERE (status = 'Chờ làm' OR status = 'Nhắc 15p') AND due_time LIKE ?
    ''', (f"{now_str}%",))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_tasks_for_pre_reminder_15m():
    """Lấy các công việc TRƯỚC 15 PHÚT để nhắc nhở lần 1"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    in_15m = (get_now() + datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        SELECT id, title, description, category, priority, due_time, user_id 
        FROM tasks 
        WHERE status = 'Chờ làm' AND due_time LIKE ?
    ''', (f"{in_15m}%",))
    rows = cursor.fetchall()
    conn.close()
    return rows

init_db()
