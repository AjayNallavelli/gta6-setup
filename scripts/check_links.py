#!/usr/bin/env python3
"""Check internal links in dist/ resolve, every Amazon link is rel=sponsored nofollow noopener, and the tag config is honoured."""
import sys, json
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parent.parent
dist = ROOT / "dist"
site = json.loads((ROOT / "site.json").read_text())
tag = json.loads((ROOT / "data/config.json").read_text()).get("amazon_tag", "")
BASE = urlparse(site["base_url"]).path.rstrip("/")
bad, n, amz = [], 0, 0
for f in dist.rglob("*.html"):
    s = BeautifulSoup(f.read_text(), "lxml")
    for tg, attr in (("a", "href"), ("link", "href"), ("script", "src"), ("img", "src")):
        for el in s.find_all(tg):
            u = el.get(attr)
            if not u or u.startswith(("mailto:", "#", "javascript:")):
                continue
            p = urlparse(u)
            if p.scheme in ("http", "https"):
                if p.netloc.endswith("amazon.in"):
                    amz += 1
                    rel = set(el.get("rel") or [])
                    if not {"sponsored", "nofollow", "noopener"} <= rel:
                        bad.append((str(f.relative_to(dist)), u + " (amazon link missing rel)"))
                    want = f"?tag={tag}" if tag else ""
                    if not (p.path.startswith("/dp/") and (p.query == (f"tag={tag}" if tag else ""))):
                        bad.append((str(f.relative_to(dist)), u + " (bad amazon url/tag)"))
                continue
            n += 1
            if p.path.startswith("/"):
                if not (p.path == BASE or p.path.startswith(BASE + "/")):
                    bad.append((str(f.relative_to(dist)), u + " (missing base path)")); continue
                path = p.path[len(BASE):] or "/"
            else:
                path = str(Path("/") / f.parent.relative_to(dist) / p.path)
            target = dist / path.lstrip("/")
            if path.endswith("/") or not target.suffix:
                target = target / "index.html" if not target.is_file() else target
            if not target.exists():
                bad.append((str(f.relative_to(dist)), u))
print(f"checked {n} internal links, {amz} amazon links across {len(list(dist.rglob('*.html')))} pages; problems: {len(bad)}")
for b in bad[:40]:
    print("  BAD", b)
sys.exit(1 if bad else 0)
