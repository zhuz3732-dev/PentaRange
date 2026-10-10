"""SSRF tiers.

low    - the URL is fetched with no checks at all
medium - the scheme is checked but the destination is not, so link-local metadata is reachable
high   - a hostname allowlist that a DNS rebind or a decimal-IP literal walks straight past
"""

import ipaddress
import socket
from urllib.parse import urlparse

import requests

from db import fetch_flag

FANG_BASE = "/challenge/ssrf"


def low(q: str, request) -> str:
    """Blind fetch. Whatever URL you hand over is requested with the server's own network access."""
    if not q:
        return (
            "试试 ?q=http://127.0.0.1:8000/\n"
            "或 ?q=http://db:3306/\n"
            "本关完全不校验目标。"
        )
    try:
        r = requests.get(q, timeout=4, allow_redirects=True)
        body = r.text[:1200]
        return (
            f"GET {q}\nHTTP {r.status_code}  ({len(r.content)} bytes)\n\n{body}\n\n"
            f"{fetch_flag('ssrf', 'low')}"
        )
    except requests.RequestException as exc:
        return f"GET {q}\n请求失败: {type(exc).__name__}: {exc}"


def medium(q: str, request) -> str:
    """http/https only. That restriction does not stop a link-local address."""
    if not q:
        return (
            "试试 ?q=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
        )
    parsed = urlparse(q)
    if parsed.scheme not in ("http", "https"):
        return f"拒绝: scheme={parsed.scheme!r}，只允许 http/https"
    try:
        r = requests.get(q, timeout=4)
        return f"GET {q}\nHTTP {r.status_code}\n\n{r.text[:1200]}\n\n{fetch_flag('ssrf', 'medium')}"
    except requests.RequestException as exc:
        return f"GET {q}\n请求失败: {type(exc).__name__}: {exc}"


def high(q: str, request) -> str:
    """The allowlist compares the *hostname string* found in the URL, then re-resolves it.

    Classic TOCTOU: the name resolves to a public address during the check and to loopback when
    ``requests`` performs the actual connection. A decimal/octal IP literal named in the allowlist
    also slips through because only the textual host is compared.
    """
    allow = {"pentarange.local", "api.pentarange.local"}
    if not q:
        return "试试 ?q=http://pentarange.local/\n本关用 hostname 白名单，只比对 URL 里的字符串。"
    parsed = urlparse(q)
    host = parsed.hostname or ""
    if host not in allow:
        try:
            # A numeric literal such as 2130706433 (== 127.0.0.1) reaches here and is treated as
            # a legitimate "public" address by this naive check.
            ip = ipaddress.ip_address(
                socket.inet_aton(host) if host.replace(".", "").isdigit() else host
            )
            if ip.is_private or ip.is_loopback:
                return f"拒绝: {host} 是内网地址"
        except (ValueError, OSError):
            return f"拒绝: {host} 不在白名单 {sorted(allow)} 中，且无法解析"
    try:
        r = requests.get(q, timeout=4)
        return f"GET {q}\nHTTP {r.status_code}\n\n{r.text[:1200]}\n\n{fetch_flag('ssrf', 'high')}"
    except requests.RequestException as exc:
        return f"GET {q}\n请求失败: {type(exc).__name__}: {exc}"
