"""PentaRange central configuration.

Everything is read from the environment so the same image runs in every tier. The defaults are
deliberately weak (fixed SECRET_KEY, debug on) because a lab that is secure by default teaches
nothing.
"""

import os


class Config:
    # --- identity -----------------------------------------------------------
    APP_NAME = "PentaRange"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8000"))

    # --- deliberately weak session/crypto material ---------------------------
    # A fixed key means a learner can forge a session cookie by hand, which is the
    # point of the JWT/cookie-forging exercises.
    SECRET_KEY = os.environ.get("SECRET_KEY", "pentarange-dev-secret-do-not-reuse")

    # --- database ------------------------------------------------------------
    DB_HOST = os.environ.get("DB_HOST", "db")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_NAME = os.environ.get("DB_NAME", "pentarange")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "PentaRange_admin_2026")

    # --- lab plumbing --------------------------------------------------------
    UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/var/www/pentarange/uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # Show the vulnerable source next to each challenge. Turning this off is one of the
    # first hardening exercises.
    SOURCE_DISCLOSURE = os.environ.get("SOURCE_DISCLOSURE", "1") == "1"

    @classmethod
    def dsn(cls) -> str:
        return (
            f"host={cls.DB_HOST} port={cls.DB_PORT} dbname={cls.DB_NAME} "
            f"user={cls.DB_USER} password={cls.DB_PASSWORD}"
        )
