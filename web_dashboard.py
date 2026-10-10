import os
import datetime
from flask import Flask, render_template, request, redirect, send_file
from config import EXCEL_PATH
from database import (
    get_pending_tasks, get_today_work_logs, get_all_tasks, 
    add_task, log_work, mark_task_completed, get_now
)
from excel_exporter import export_to_excel

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    tasks = get_pending_tasks()
    today_logs = get_today_work_logs()
    all_tasks = get_all_tasks()

    total_tasks = len(all_tasks)
    completed_tasks = len([t for t in all_tasks if t[4] == 'Hoàn thành'])
    pending_tasks = len(tasks)
    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

    return render_template(
        'index.html',
        tasks=tasks,
        today_logs=today_logs,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        completion_rate=completion_rate
    )

@app.route('/api/add-task', methods=['POST'])
def api_add_task():
    title = request.form.get('title')
    priority = request.form.get('priority', 'Trung bình')
    due_time_raw = request.form.get('due_time', '').strip()

    now = get_now()
    due_time_str = None
    if due_time_raw:
        if len(due_time_raw) <= 5 and ':' in due_time_raw:
            due_time_str = f"{now.strftime('%Y-%m-%d')} {due_time_raw}:00"
        else:
            due_time_str = due_time_raw

    if title:
        add_task(title=title, priority=priority, due_time=due_time_str)
        export_to_excel()

    return redirect('/')

@app.route('/api/log-work', methods=['POST'])
def api_log_work():
    content = request.form.get('content')
    if content:
        log_work(content=content)
        export_to_excel()

    return redirect('/')

@app.route('/api/complete-task/<int:task_id>', methods=['POST'])
def api_complete_task(task_id):
    mark_task_completed(task_id)
    export_to_excel()
    return redirect('/')

@app.route('/download-excel')
def download_excel():
    export_to_excel()
    if os.path.exists(EXCEL_PATH):
        return send_file(EXCEL_PATH, as_attachment=True, download_name="Quan_Ly_Cong_Viec.xlsx")
    return "File not found", 404

if __name__ == '__main__':
    print("Starting Web Dashboard on http://localhost:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
