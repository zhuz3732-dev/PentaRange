"""Challenge registry.

Each module exposes one callable per tier:

    def low(q: str, request) -> str
    def medium(q: str, request) -> str
    def high(q: str, request) -> str

``q`` is the raw ``?q=`` value (never sanitised here on purpose) and ``request`` is the live Flask
request, so modules that need POST bodies, headers or cookies can reach them.
"""
from . import deserialize, sqli, ssrf, upload, xss

REGISTRY = {}

for _module in (sqli, xss, upload, ssrf, deserialize):
    _level = _module.__name__.rsplit(".", 1)[-1]
    for _tier in ("low", "medium", "high"):
        _fn = getattr(_module, _tier, None)
        if _fn is not None:
            REGISTRY[(_level, _tier)] = _fn

__all__ = ["REGISTRY"]