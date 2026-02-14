import sqlite3
from flask import g, current_app
import config


def get_db():
    if "db" not in g:
        if config.TURSO_DATABASE_URL:
            import libsql_experimental as libsql
            g.db = libsql.connect(
                database=config.TURSO_DATABASE_URL,
                auth_token=config.TURSO_AUTH_TOKEN,
            )
            g.db.row_factory = sqlite3.Row
        else:
            g.db = sqlite3.connect(current_app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
