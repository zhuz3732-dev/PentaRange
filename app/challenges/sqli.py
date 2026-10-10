"""SQL injection tiers.

low    - classic UNION-based, error messages leaked to the page
medium - the query is wrapped in a way that hides output; boolean/time blind only
high   - a naive keyword blacklist sits in front of the same concatenation
"""
from db import fetch_flag, raw_cursor


def low(q: str, request) -> str:
    """The stock vulnerable pattern: the input is glued straight into the statement."""
    if not q:
        return "试试 ?q=1"
    sql = "SELECT id, username, email FROM users WHERE id = " + q
    with raw_cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return sql + "\n\n" + _table(rows, "low")


def medium(q: str, request) -> str:
    """Only a boolean leaks: the page tells you whether the row count changed, nothing more."""
    if not q:
        return "试试 ?q=1"
    sql = (
        "SELECT COUNT(*) AS n FROM users WHERE username = '" + q + "'"
    )
    with raw_cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
    n = row["n"] if row else 0
    # The classic tell. No data echoed, only truthiness.
    hit = f"用户存在\n\n{fetch_flag('sqli', 'medium')}\n" if n > 0 else "用户不存在\n"
    # Boolean blind: the payload itself is never reflected, so only the branch is observable.
    return hit


def high(q: str, request) -> str:
    """A blacklist that only looks at the raw string, and only lists five keywords.

    ``or`` is not on the list, so a boolean tautology walks straight through without needing
    ``union`` or ``select`` at all. That is the lesson: enumerating bad words is not validation.
    """
    if not q:
        return "试试 ?q=1"
    banned = ["union", "select", "from", "where", "1=1"]
    probe = q.lower()
    for b in banned:
        if b in probe:
            return f"拦截：检测到关键字 {b!r}"
    sql = "SELECT id, username, email FROM users WHERE id = " + q
    with raw_cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return sql + "\n\n" + _table(rows, "high")

def _table(rows, tier: str) -> str:
    if not rows:
        return "(无结果)"
    out = [" | ".join(str(v) for v in rows[0].keys())]
    for r in rows:
        out.append(" | ".join(str(v) for v in r.values()))
    out.append("")
    out.append(f"-- 共 {len(rows)} 行")
    out.append(f"-- 本关 flag: {fetch_flag('sqli', tier)}")
    return "\n".join(out)