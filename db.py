import os
import re
import pymysql
from pymysql.cursors import DictCursor

# Motor: PostgreSQL si hay DATABASE_URL (o GYMPRO_DB_ENGINE=postgres); MySQL/MariaDB en caso contrario.
DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_PG = os.getenv("GYMPRO_DB_ENGINE", "").lower() in ("postgres", "postgresql", "pg") or DATABASE_URL.startswith(("postgres://", "postgresql://"))

DB_CONFIG = {
    "host": os.getenv("GYMPRO_DB_HOST", "localhost"),
    "port": int(os.getenv("GYMPRO_DB_PORT", "5432" if IS_PG else "3306")),
    "user": os.getenv("GYMPRO_DB_USER", "postgres" if IS_PG else "root"),
    "password": os.getenv("GYMPRO_DB_PASSWORD", ""),
    "database": os.getenv("GYMPRO_DB_NAME", "gimnasio"),
    "cursorclass": DictCursor,
    "autocommit": True,
    "charset": "utf8mb4",
}


class _Row(dict):
    """Fila tipo diccionario; permite leer claves en mayusculas (r["COLUMN_NAME"]) aunque PostgreSQL las devuelva en minusculas."""
    def __missing__(self, key):
        if isinstance(key, str):
            for k in (key.lower(), key.upper()):
                if k in self:
                    return dict.__getitem__(self, k)
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


def _translate(sql):
    """Adapta el SQL escrito para MySQL a PostgreSQL."""
    sql = sql.replace("`", '"')
    sql = re.sub(r"SHOW\s+TABLES\s+LIKE\s+('[^']*')",
                 r"SELECT table_name FROM information_schema.tables WHERE table_schema=current_schema() AND table_name ILIKE \1", sql, flags=re.I)
    sql = re.sub(r"DATABASE\(\)", "current_database()", sql, flags=re.I)
    sql = re.sub(r"TABLE_SCHEMA\s*=\s*%s", "%s IS NOT NULL AND TABLE_SCHEMA=current_schema()", sql, flags=re.I)
    sql = re.sub(r",\s*COLUMN_TYPE\b", ", udt_name AS column_type", sql, flags=re.I)
    sql = re.sub(r"CURDATE\(\)", "CURRENT_DATE", sql, flags=re.I)
    sql = re.sub(r"DATE_FORMAT\(\s*CURRENT_DATE\s*,\s*'%+Y-%+m-01'\s*\)", "date_trunc('month', CURRENT_DATE)", sql, flags=re.I)
    sql = re.sub(r"DATE_(ADD|SUB)\(\s*(.+?)\s*,\s*INTERVAL\s+(\d+)\s+(\w+)\s*\)",
                 lambda m: f"({m.group(2)}::date {'+' if m.group(1).upper() == 'ADD' else '-'} INTERVAL '{m.group(3)} {m.group(4).lower()}')", sql, flags=re.I)
    sql = re.sub(r"AS\s+CHAR\)", "AS TEXT)", sql, flags=re.I)
    sql = re.sub(r"\bLIKE\b", "ILIKE", sql, flags=re.I)
    return sql


class _PgCursor:
    def __init__(self, conn):
        self._conn = conn
        self._cur = conn.cursor()

    def execute(self, sql, params=None):
        self._cur.execute(_translate(sql), tuple(params) if params else None)
        return self

    def _wrap(self, row):
        return _Row(row) if row is not None else None

    def fetchone(self):
        return self._wrap(self._cur.fetchone())

    def fetchall(self):
        return [_Row(r) for r in self._cur.fetchall()]

    @property
    def lastrowid(self):
        try:
            c = self._conn.cursor()
            c.execute("SELECT lastval() AS id")
            return c.fetchone()["id"]
        except Exception:
            return None

    def __getattr__(self, name):
        return getattr(self._cur, name)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._cur.close()


class _PgConnection:
    """Expone la misma interfaz que usa el proyecto con PyMySQL (cursor, begin, commit, rollback, close)."""
    def __init__(self, conn):
        self._conn = conn
        self._conn.autocommit = True

    def cursor(self):
        return _PgCursor(self._conn)

    def begin(self):
        self._conn.autocommit = False

    def commit(self):
        self._conn.commit()
        self._conn.autocommit = True

    def rollback(self):
        self._conn.rollback()
        self._conn.autocommit = True

    def close(self):
        self._conn.close()


def get_db():
    if IS_PG:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            kw = dict(host=DB_CONFIG["host"], port=DB_CONFIG["port"], user=DB_CONFIG["user"],
                      password=DB_CONFIG["password"], dbname=DB_CONFIG["database"], cursor_factory=RealDictCursor)
            if os.getenv("GYMPRO_DB_SSLMODE"):
                kw["sslmode"] = os.getenv("GYMPRO_DB_SSLMODE")
            conn = psycopg2.connect(**kw)
        return _PgConnection(conn)
    return pymysql.connect(**{k: v for k, v in DB_CONFIG.items()})


def table_columns(conn, table):
    with conn.cursor() as cur:
        if IS_PG:
            cur.execute("""
                SELECT column_name AS "COLUMN_NAME", data_type AS "DATA_TYPE", is_nullable AS "IS_NULLABLE",
                       column_default AS "COLUMN_DEFAULT",
                       CASE WHEN is_identity='YES' OR column_default LIKE 'nextval%%' THEN 'auto_increment' ELSE '' END AS "EXTRA"
                FROM information_schema.columns
                WHERE table_schema=current_schema() AND table_name=%s
                ORDER BY ordinal_position
            """, (table,))
        else:
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
