import os

UISP_BASE_URL = os.environ.get("UISP_BASE_URL", "https://uispdev.pnw.net/crm/api/v1.0")
UISP_API_TOKEN = os.environ.get("UISP_API_TOKEN", "")
MAPBOX_TOKEN = os.environ.get("MAPBOX_TOKEN", "")
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "canvass.db"))
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
