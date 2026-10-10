"""File upload tiers.

low    - anything goes, extensions included
medium - only the Content-Type header is inspected, and it is attacker-controlled
high   - extension blacklist plus .htaccess override
"""

import os


from config import Config
from db import fetch_flag
from werkzeug.utils import secure_filename


def low(q: str, request) -> str:
    """No validation beyond ``secure_filename``, which happily keeps ``.php`` and ``.py``."""
    if not request.files:
        return (
            "POST 上传表单字段名 file。\n"
            "注意：这里只做了 secure_filename，扩展名完全不查。\n"
            "上传后路径：/uploads/<你的文件名>，执行入口 http://127.0.0.1:8081/<你的文件名>"
        )
    f = request.files.get("file")
    if not f:
        return "没有收到文件（字段名必须是 file）"
    name = secure_filename(f.filename) or "upload.bin"
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    path = os.path.join(Config.UPLOAD_DIR, name)
    f.save(path)
    return (
        f"已保存: {path}\n"
        f"URL: /uploads/{name}\n"
        f"扩展名未做任何检查 —— {fetch_flag('upload', 'low')}"
    )


def medium(q: str, request) -> str:
    """Only ``Content-Type`` is checked. The client sends that header, so it is a formality."""
    f = request.files.get("file")
    if not f:
        return "没有收到文件（字段名必须是 file）。本关只检查 Content-Type。"
    allowed = {"image/png", "image/jpeg", "image/gif"}
    if f.mimetype not in allowed:
        return f"拒绝: Content-Type={f.mimetype} 不在 {sorted(allowed)} 中"
    name = secure_filename(f.filename) or "upload.bin"
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    f.save(os.path.join(Config.UPLOAD_DIR, name))
    return (
        f"已保存: /uploads/{name}\n"
        f"Content-Type 是客户端自己发的，改个 header 就过了 —— {fetch_flag('upload', 'medium')}"
    )


def high(q: str, request) -> str:
    """Blacklist plus an ``.htaccess`` escape hatch. ``.htaccess`` is not in the blacklist."""
    f = request.files.get("file")
    if not f:
        return (
            "没有收到文件（字段名必须是 file）。\n"
            "本关黑名单: php, php3, phtml, asp, aspx, jsp。\n"
            "想想有没有别的办法让服务器执行上传的东西。"
        )
    name = secure_filename(f.filename) or "upload.bin"
    blocked = (".php", ".php3", ".phtml", ".asp", ".aspx", ".jsp")
    if name.lower().endswith(blocked):
        return f"拒绝: {name} 命中扩展名黑名单 {blocked}"
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    f.save(os.path.join(Config.UPLOAD_DIR, name))
    return (
        f"已保存: /uploads/{name}\n"
        f"黑名单只挡了直接可执行的扩展名。.htaccess / .user.ini 不在名单里 —— "
        f"{fetch_flag('upload', 'high')}"
    )
