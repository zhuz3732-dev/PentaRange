"""XSS tiers.

low    - reflected with no encoding whatsoever
medium - stored, and the admin bot endpoint reads the cookie back
high   - a DOM sink that never returns to the server
"""

import html

from db import raw_cursor


def low(q: str, request) -> str:
    """Echoed raw. ``<script>`` and attributes both work."""
    if not q:
        return "试试 ?q=<b>hi</b>"
    return f"你搜索了：{q}"


def medium(q: str, request) -> str:
    """Stored, but only through POST.

    The write has to be a POST because a stored payload is supposed to arrive from the victim's own
    browser (a comment box), not from a link the attacker sends. The defect is that the stored
    value is handed back to the template with ``|safe`` and rendered unescaped.
    """
    action = "已保存" if request.method == "POST" else "当前列表"

    if q and request.method == "POST":
        with raw_cursor() as cur:
            cur.execute(
                "INSERT INTO notes (user_id, title, body) VALUES (1, 'guest', %s)", (q,)
            )
    with raw_cursor() as cur:
        cur.execute("SELECT id, title, body FROM notes ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()

    listing = "\n".join(f"#{r['id']} [{r['title']}] {r['body']}" for r in rows)
    return f"{action}（最多 10 条）：\n{listing}"


def high(q: str, request) -> str:
    """The server encodes everything. The vulnerability is on the client, in the DOM sink.

    The returned HTML is safe server-side; the template that consumes it inserts the decoded
    value with ``innerHTML``. Encoding on the way out is not the same as encoding on the way in.
    """
    if not q:
        return "试试 ?q=<img src=x onerror=alert(1)>"
    # Server-side escaping - correct, and irrelevant to the DOM sink.
    safe = html.escape(q)
    return (
        "服务端已转义：\n" + safe + "\n\n"
        "但页面的 JS 会把 URL 里的原始 q 参数 decodeURIComponent 后写入 innerHTML，"
        "转义在这里帮不上忙。"
    )
