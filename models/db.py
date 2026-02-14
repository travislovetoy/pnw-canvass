import sqlite3
from flask import g, current_app
import config


class Row:
    """Dict-like row compatible with sqlite3.Row interface."""
    def __init__(self, columns, values):
        self._columns = columns
        self._values = values
        self._map = dict(zip(columns, values))

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self._values[key]
        return self._map[key]

    def __contains__(self, key):
        return key in self._map

    def keys(self):
        return self._columns


class CursorWrapper:
    """Wraps a libsql cursor to return Row objects."""
    def __init__(self, cursor):
        self._cursor = cursor
        self._columns = None

    def _get_columns(self):
        if self._columns is None and self._cursor.description:
            self._columns = [desc[0] for desc in self._cursor.description]
        return self._columns

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        cols = self._get_columns()
        return Row(cols, row) if cols else row

    def fetchall(self):
        rows = self._cursor.fetchall()
        cols = self._get_columns()
        if cols:
            return [Row(cols, row) for row in rows]
        return rows

    def __iter__(self):
        cols = self._get_columns()
        for row in self._cursor:
            yield Row(cols, row) if cols else row


class ConnectionWrapper:
    """Wraps a libsql connection to return Row-wrapped cursors."""
    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=()):
        cursor = self._conn.execute(sql, params)
        return CursorWrapper(cursor)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db():
    if "db" not in g:
        if config.TURSO_DATABASE_URL:
            import libsql_experimental as libsql
            conn = libsql.connect(
                database=config.TURSO_DATABASE_URL,
                auth_token=config.TURSO_AUTH_TOKEN,
            )
            g.db = ConnectionWrapper(conn)
        else:
            g.db = sqlite3.connect(current_app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
