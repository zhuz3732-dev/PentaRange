"""Shared database helpers.

Two access styles live side by side on purpose:

* ``raw_cursor``  - hands out a cursor and lets the caller build SQL by string interpolation.
                    This exists so the vulnerability modules have something honest to be
                    vulnerable with. The ``high`` tiers route their payload through
                    ``raw_cursor`` without any escaping at all.
* ``safe_cursor`` - parameterised helper used by the ``secure`` variants that live on the
                    ``hardened`` branch.

Keeping both in one module makes the diff between vulnerable and fixed code small and readable,
which is what a learner needs to see.
"""
import contextlib
import time

import pymysql

from config import Config


def connect():
    """Open a new connection. Retries because compose may start us before MySQL is ready."""
    last = None
    for attempt in range(30):
        try:
            return pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
            )
        except Exception as exc:  # noqa: BLE001 - lab code, surface anything
            last = exc
            time.sleep(1)
    raise RuntimeError(f"cannot reach MySQL at {Config.DB_HOST}:{Config.DB_PORT}: {last}")


@contextlib.contextmanager
def raw_cursor():
    """A cursor with no safety rails. Callers interpolate strings into SQL themselves."""
    conn = connect()
    try:
        with conn.cursor() as cur:
            yield cur
    finally:
        conn.close()


@contextlib.contextmanager
def safe_cursor():
    """A cursor plus a parameterised ``query`` closure. This is the fixed pattern."""
    conn = connect()
    try:
        with conn.cursor() as cur:
            def query(sql, params=None):
                cur.execute(sql, params or ())
                return cur.fetchall()
            yield query
    finally:
        conn.close()


def fetch_flag(level: str, tier: str) -> str:
    with raw_cursor() as cur:
        cur.execute("SELECT flag FROM flags WHERE level=%s AND tier=%s", (level, tier))
        row = cur.fetchone()
    return row["flag"] if row else "FLAG{not_seeded}"