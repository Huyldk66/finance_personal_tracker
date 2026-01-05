from pathlib import Path
from platformdirs import user_data_dir




APP_NAME   = "__fainance_personal__"
APP_AUTHOR = "tiensthienvo"  


APP_DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)


# DATA_FILE = Path(__file__).parent / "transactions.csv"
# BACKUP_FOLDER = Path(__file__).parent / "backups"

# DATA_FILE = Path("debts.json")
# DATA_FILE      = Path("debts.json")
# PAYMENT_LOG    = Path("payment_log.json")
# SCHEDULE_FILE  = Path("schedule_export.csv")


# BASE_DIR = Path(__file__).parent
# FILE_NOTES   = BASE_DIR / "notes.json"
# FILE_TODOS   = BASE_DIR / "todos.json"
# FILE_MARKERS = BASE_DIR / "markers.csv"
# FILE_TOKEN   = BASE_DIR / "token.json"

# FILE_CRED    = BASE_DIR / "credentials.json"



# TRANS_CSV = BASE_DIR / "transactions.csv"
# LOAN_CSV  = BASE_DIR / "loans.csv"

#data 
BASE_DIR = APP_DATA_DIR /  "data"
BASE_DIR.mkdir(parents=True, exist_ok=True)

#dataa=manager  # backup
BACKUP_DIR = APP_DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# engine nợ
FILE_FUNDS = BASE_DIR / "budget_personal.json"
FILE_GOALS = BASE_DIR / "budget_group.json"

# hũ tiền 
DATA_BUDGET =  BASE_DIR / "budget_data.json"


#calendar 
DATA_TODOS = BASE_DIR / "todos.json"
DATA_NOTES = BASE_DIR / "notes.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    'openid'
]
# toekn google 
FILE_TOKEN  = BASE_DIR / "token.json"
FILE_CRED  = Path(__file__).parent / 'credentials.json'

# nợ
DEBT_DATA = BASE_DIR / "debts.json"
PAYMENT_LOG = BASE_DIR / "payment_log.json"
SCHEDULE_FILE =  BASE_DIR / "schedule_export.csv"


# giao dịch 
TRANSACTION_DATA = BASE_DIR / "transactions.csv"


THEMES_DEBT_PAGE = {
    "spring": {
        "name": "Xuân (Tết & May mắn)",
        "bg_primary": "#FFFDF5",   # Kem ấm nhẹ (thay vì vàng chói)
        "bg_secondary": "#C62828", # Đỏ nhung sang trọng
        "accent": "#FFC107",       # Vàng hổ phách (Gold)
        "text_main": "#4E342E",    # Nâu đậm (dễ đọc hơn đen tuyền trên nền kem)
        "text_light": "#FFFFFF",
        "btn_hover": "#D32F2F"     # Đỏ tươi hơn khi hover
    },
    "summer": {
        "name": "Hạ (Biển & Năng lượng)",
        "bg_primary": "#F0F9FF",   # Xanh dương siêu nhạt (mát mắt)
        "bg_secondary": "#0277BD", # Xanh biển sâu (Ocean Blue)
        "accent": "#00BCD4",       # Cyan/Turquoise tươi mát
        "text_main": "#014377",    # Xanh than đậm
        "text_light": "#FFFFFF",
        "btn_hover": "#0288D1"     # Xanh sáng hơn khi hover
    },
    "autumn": {
        "name": "Thu (Lá & Ấm áp)",
        "bg_primary": "#FEF5E7",   # Màu vỏ trứng/Linen
        "bg_secondary": "#D84315", # Cam đất nung (Terracotta)
        "accent": "#F57C00",       # Cam bí ngô
        "text_main": "#3E2723",    # Nâu Cafe
        "text_light": "#FFFFFF",
        "btn_hover": "#E64A19"     # Cam đậm hơn chút khi hover
    },
    "winter": {
        "name": "Đông (Tuyết & Sang trọng)",
        "bg_primary": "#F5F7FA",   # Xám trắng lạnh
        "bg_secondary": "#37474F", # Xám xanh đá phiến (Blue Grey)
        "accent": "#607D8B",       # Xám thép (Steel)
        "text_main": "#263238",    # Đen xám
        "text_light": "#FFFFFF",
        "btn_hover": "#455A64"     # Xám xanh sáng hơn
    }
}


THEMES_CALENDAR_PAGE = {
    "spring": {"name": "Xuân", "bg": "#FFF8E1", "sec": "#b30000", "acc": "#FFD700", "txt": "#5D4037", "btn": "#d91e18"},
    "summer": {"name": "Hạ", "bg": "#E1F5FE", "sec": "#0277BD", "acc": "#4FC3F7", "txt": "#01579B", "btn": "#0288d1"},
    "autumn": {"name": "Thu", "bg": "#FFF3E0", "sec": "#E65100", "acc": "#FFB74D", "txt": "#3E2723", "btn": "#f57c00"},
    "winter": {"name": "Đông", "bg": "#ECEFF1", "sec": "#263238", "acc": "#90A4AE", "txt": "#37474F", "btn": "#455A64"}
}