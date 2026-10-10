import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Settings
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS", "")  # Empty means all users allowed, or comma-separated list of IDs
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL", "")


# Timezone
TIMEZONE = os.getenv("TIMEZONE", "Asia/Ho_Chi_Minh")

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "tasks.db")
EXCEL_PATH = os.path.join(BASE_DIR, "Quan_Ly_Cong_Viec.xlsx")

# Ensure data directory exists
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
