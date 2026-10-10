"""Deserialisation tiers.

low    - ``pickle.loads`` on attacker input: direct RCE
medium - ``yaml.load`` with the default loader: ``!!python/object/apply`` reaches any callable
high   - attribute injection into an object that is later consumed by a dangerous sink
"""
import base64
import pickle

import yaml

from db import fetch_flag


def low(q: str, request) -> str:
    """The payload arrives base64-encoded in ``q`` and goes straight into pickle."""
    if not q:
        sample = base64.b64encode(pickle.dumps({"user": "guest", "role": "user"})).decode()
        return (
            "把 pickle 字节 base64 后放进 ?q=\n"
            f"当前默认值: {sample}\n"
            "pickle.loads 在反序列化时就执行 __reduce__，不需要任何额外条件。"
        )
    try:
        raw = base64.b64decode(q, validate=True)
    except Exception as exc:  # noqa: BLE001
        return f"base64 解码失败: {exc}"
    try:
        obj = pickle.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return f"pickle.loads 抛出: {type(exc).__name__}: {exc}"
    return f"反序列化结果: {obj!r}\n\n{fetch_flag('deserialize', 'low')}"


def medium(q: str, request) -> str:
    """``yaml.load`` without ``SafeLoader``. The tag carries the payload."""
    if not q:
        return (
            "试试 ?q=!!python/object/apply:os.system ['id']\n"
            "这里用的是 yaml.load(stream) 默认 Loader。"
        )
    try:
        data = yaml.load(q)
    except Exception as exc:  # noqa: BLE001
        return f"yaml.load 抛出: {type(exc).__name__}: {exc}"
    return f"解析结果: {data!r}\n\n{fetch_flag('deserialize', 'medium')}"


def high(q: str, request) -> str:
    """Untrusted YAML builds an object graph whose ``path`` attribute is later read by a sink.

    ``yaml.load`` constructs whatever class the document names. Pointing the attribute at a file
    the process can read turns the "config parser" into an arbitrary file read.
    """
    if not q:
        return (
            "试试构造一个带 path 属性的对象：\n"
            "!!python/object/apply:types.SimpleNamespace\n"
            "  kwargs: {path: /etc/passwd}"
        )
    try:
        cfg = yaml.load(q)
    except Exception as exc:  # noqa: BLE001
        return f"yaml.load 抛出: {type(exc).__name__}: {exc}"
    path = getattr(cfg, "path", None)
    if not path:
        return f"解析结果: {cfg!r}\n（没有 path 属性，sink 没触发）"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            body = fh.read(2000)
        return f"读取 {path}:\n\n{body}\n\n{fetch_flag('deserialize', 'high')}"
    except OSError as exc:
        return f"读取 {path} 失败: {exc}"