from flask import Flask
import config
from models.db import close_db

from routes.auth import bp as auth_bp
from routes.api_leads import bp as leads_bp
from routes.api_visits import bp as visits_bp
from routes.api_territories import bp as territories_bp
from routes.api_reps import bp as reps_bp
from routes.api_dashboard import bp as dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["DB_PATH"] = config.DB_PATH
    app.config["UISP_BASE_URL"] = config.UISP_BASE_URL
    app.config["UISP_API_TOKEN"] = config.UISP_API_TOKEN

    app.teardown_appcontext(close_db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(visits_bp)
    app.register_blueprint(territories_bp)
    app.register_blueprint(reps_bp)
    app.register_blueprint(dashboard_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5050)
