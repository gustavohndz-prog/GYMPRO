import os
import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    "host": os.getenv("GYMPRO_DB_HOST", "localhost"),
    "user": os.getenv("GYMPRO_DB_USER", "root"),
    "password": os.getenv("GYMPRO_DB_PASSWORD", ""),
    "database": os.getenv("GYMPRO_DB_NAME", "gimnasio"),
    "cursorclass": DictCursor,
    "autocommit": True,
    "charset": "utf8mb4",
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

def table_columns(conn, table):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
            ORDER BY ORDINAL_POSITION
        """, (DB_CONFIG["database"], table))
        return cur.fetchall()

def columns_set(conn, table):
    return {r["COLUMN_NAME"] for r in table_columns(conn, table)}

def first_existing(columns, *names):
    for name in names:
        if name in columns:
            return name
    return None
