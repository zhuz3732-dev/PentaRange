"""PentaRange entry point."""
import os
import sys
import traceback

# Make ``python main.py`` and ``flask run`` resolve the sibling modules identically. This has to
# happen before the local imports below.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, abort, render_template, request  # noqa: E402

from config import Config  # noqa: E402
from challenges import REGISTRY  # noqa: E402

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH

# Where the learner-facing metadata for the index page comes from. Keep this next to REGISTRY so
# adding a module means touching exactly two places.
LEVEL_INFO = {
    "sqli": {
        "title": "SQL 注入",
        "summary": "字符串拼接查询",
        "tiers": {
            "low": "用 union 把 users.secret 读出来",
            "medium": "无回显：布尔盲注或时间盲注",
            "high": "有关键字过滤，需要绕过",
        },
    },
    "xss": {
        "title": "跨站脚本",
        "summary": "反射 / 存储 / DOM",
        "tiers": {
            "low": "直接反射，无编码",
            "medium": "存储型，偷 admin 的 cookie",
            "high": "前端 DOM sink",
        },
    },
    "upload": {
        "title": "文件上传",
        "summary": "扩展名 / MIME / .htaccess",
        "tiers": {
            "low": "不限制扩展名，直接传 webshell",
            "medium": "只查 Content-Type，伪造即可",
            "high": "黑名单绕过 + .htaccess 覆盖",
        },
    },
    "ssrf": {
        "title": "服务端请求伪造",
        "summary": "内网探测 / 元数据 / DNS 重绑定",
        "tiers": {
            "low": "探测内网端口",
            "medium": "读云元数据 169.254.169.254",
            "high": "绕过 host 白名单",
        },
    },
    "deserialize": {
        "title": "反序列化",
        "summary": "pickle / YAML / 对象注入",
        "tiers": {
            "low": "pickle 直接 RCE",
            "medium": "yaml.load 不安全解析",
            "high": "对象属性注入到危险 sink",
        },
    },
}

# Absolute path of this package, used by the /source browser.
APP_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return render_template("index.html", levels=LEVEL_INFO)


@app.route("/challenge/<level>/<tier>", methods=["GET", "POST"])
def challenge(level: str, tier: str):
    key = (level, tier)
    handler = REGISTRY.get(key)
    if handler is None:
        abort(404, description=f"unknown challenge {level}/{tier}")

    q = request.values.get("q", "")
    result = None
    error = None
    try:
        result = handler(q, request)
    except Exception as exc:  # noqa: BLE001 - a lab must show its stack traces
        error = f"{type(exc).__name__}: {exc}"
        result = traceback.format_exc() if Config.DEBUG else "internal error"

    source = None
    if Config.SOURCE_DISCLOSURE:
        source = _read_source_for(level)

    return render_template(
        "challenge.html",
        level=level,
        tier=tier,
        title=LEVEL_INFO.get(level, {}).get("title", level),
        goal=LEVEL_INFO.get(level, {}).get("tiers", {}).get(tier, ""),
        q=q,
        result=result,
        error=error,
        source=source,
    )

def _read_source_for(level: str) -> str:
    path = os.path.join(APP_DIR, "challenges", f"{level}.py")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return "(source unavailable)"


@app.route("/source")
@app.route("/source/")
def source_list():
    """Deliberate source disclosure. One of the first things to lock down on the hardened branch."""
    if not Config.SOURCE_DISCLOSURE:
        abort(404)
    files = sorted(
        f for f in os.listdir(os.path.join(APP_DIR, "challenges"))
        if f.endswith(".py") and f != "__init__.py"
    )
    return render_template("source_list.html", files=files)


@app.route("/source/<path:name>")
def source_view(name: str):
    if not Config.SOURCE_DISCLOSURE:
        abort(404)
    # Path traversal is intentionally NOT filtered here; it is part of the "high" tier of the
    # source-disclosure exercise on the hardened branch.
    target = os.path.join(APP_DIR, "challenges", name)
    try:
        with open(target, "r", encoding="utf-8") as fh:
            body = fh.read()
    except OSError as exc:
        abort(404, description=str(exc))
    return render_template("source_view.html", name=name, body=body)


@app.route("/uploads/<path:name>")
def uploads(name: str):
    """Serve what the learner uploaded.

    This route exists so the file-upload challenges have a reachable URL. It serves bytes only;
    nothing here executes anything. Execution - which is the whole point of the upload exercise -
    happens on the ``webshell`` service (Apache + mod_php) that mounts the same uploads volume.
    """
    from flask import send_from_directory

    return send_from_directory(Config.UPLOAD_DIR, name, conditional=True)


@app.route("/api/users")
def api_users():
    """Unauthenticated dump of the users table. Teaches that an internal API is still an API."""
    from db import safe_cursor

    with safe_cursor() as query:
        rows = query("SELECT id, username, email, role FROM users ORDER BY id")
    return {"count": len(rows), "users": rows}


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)