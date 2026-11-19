"""Shared helpers: data loading and the single affiliate-link function."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    return json.loads((ROOT / name).read_text())


def amazon_url(asin, tag=None):
    """The only place an Amazon link is built: https://www.amazon.in/dp/<ASIN>[?tag=<amazon_tag>]."""
    if tag is None:
        tag = load("data/config.json").get("amazon_tag", "")
    return f"https://www.amazon.in/dp/{asin}" + (f"?tag={tag}" if tag else "")


def inr(n):
    """Indian digit grouping: 1234567 -> 12,34,567."""
    n = int(round(n))
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if n < 0 else "") + "₹" + s
