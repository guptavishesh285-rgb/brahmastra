"""
db.py — Database layer for SurakshaYatra
-----------------------------------------
Runs on SQLite with zero setup when no MySQL env vars are set (great for
local dev / quick demos). Set MYSQL_HOST (and friends) and it switches
to real MySQL automatically — same table names, same query shapes.

Env vars for MySQL mode:
    MYSQL_HOST
    MYSQL_PORT      (default 3306)
    MYSQL_USER
    MYSQL_PASSWORD
    MYSQL_DB
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "surakshayatra.db")

USE_MYSQL = bool(os.environ.get("MYSQL_HOST"))

if USE_MYSQL:
    import pymysql
    import pymysql.cursors

    MYSQL_CONFIG = dict(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ.get("MYSQL_PORT", 3306)),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DB", "surakshayatra"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


class DBConnection:
    """
    Thin wrapper so the rest of app.py can write ONE set of queries that
    work on both backends. Placeholders always use '?' in application
    code; this layer translates to '%s' for MySQL.
    """

    def __init__(self):
        if USE_MYSQL:
            self.conn = pymysql.connect(**MYSQL_CONFIG)
        else:
            self.conn = sqlite3.connect(SQLITE_PATH)
            self.conn.row_factory = sqlite3.Row

    def _translate(self, query):
        return query.replace("?", "%s") if USE_MYSQL else query

    def execute(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(self._translate(query), params)
        return cur

    def executemany(self, query, seq_of_params):
        cur = self.conn.cursor()
        cur.executemany(self._translate(query), seq_of_params)
        return cur

    def executescript(self, script):
        # sqlite3 has executescript(); MySQL needs statements run one by one.
        if USE_MYSQL:
            cur = self.conn.cursor()
            for statement in script.split(";"):
                statement = statement.strip()
                if statement:
                    cur.execute(statement)
        else:
            self.conn.executescript(script)

    def fetchone(self, query, params=()):
        cur = self.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self, query, params=()):
        cur = self.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def get_db():
    return DBConnection()
