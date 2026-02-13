import os
from dotenv import load_dotenv

load_dotenv()

UISP_BASE_URL = os.environ.get("UISP_BASE_URL", "https://uispdev.pnw.net/crm/api/v1.0")
UISP_API_TOKEN = os.environ.get("UISP_API_TOKEN", "")
MAPBOX_TOKEN = os.environ.get("MAPBOX_TOKEN", "")
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "canvass.db"))
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
APP_URL = os.environ.get("APP_URL", "http://localhost:5050")
