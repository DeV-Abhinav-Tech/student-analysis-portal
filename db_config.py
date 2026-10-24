import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "student_db.sqlite")

class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        # Convert MySQL %s placeholder to SQLite ? placeholder
        transformed_query = query.replace("%s", "?")
        if params is not None:
            return self._cursor.execute(transformed_query, params)
        return self._cursor.execute(transformed_query)

    def executemany(self, query, seq_of_params):
        transformed_query = query.replace("%s", "?")
        return self._cursor.executemany(transformed_query, seq_of_params)

    def fetchone(self):
        row = self._cursor.fetchone()
        return tuple(row) if row is not None else None

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [tuple(r) for r in rows]

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    def close(self):
        self._cursor.close()

class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return SQLiteCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

def get_connection():
    try:
        import mysql.connector
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="student_db", connection_timeout=1)
        return conn
    except Exception:
        # Fallback to local SQLite database seeded from student_db.sql
        conn = sqlite3.connect(DB_PATH)
        return SQLiteConnectionWrapper(conn)