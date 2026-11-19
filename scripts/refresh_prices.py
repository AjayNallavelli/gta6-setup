#!/usr/bin/env python3
"""Re-check Amazon.in prices for every product in data/products.json (polite: one request at a time, ~3s apart).

Rules:
- A price is only updated from a product page that loaded (HTTP 200, no captcha, ASIN title present).
- If Amazon blocks or errors, the last good price and its date are kept untouched (the site shows the date).
- If the page loads and says the item is unavailable / shows no price, price becomes null ("Check price"); the previous
  value is kept in last_price / last_price_date.
- Products with ignore_price=true (implausible third-party-only prices) never get a price.
Usage: python scripts/refresh_prices.py [--only ASIN,ASIN] [--no-fx]
"""
import json, re, sys, time
from datetime import date
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parent.parent
PRICE_SEL = ["#corePriceDisplay_desktop_feature_div span.priceToPay span.a-offscreen", "#corePrice_feature_div span.a-offscreen",
             "span.priceToPay span.a-offscreen", "#apex_desktop span.a-offscreen"]


IN_STOCK = re.compile(r"in stock|only \d+ left|usually dispatched", re.I)


def in_stock(avail):
    return bool(avail) and "unavailable" not in avail.lower() and bool(IN_STOCK.search(avail))


def fetch(asin):
    from curl_cffi import requests
    last = None
    for attempt in range(2):
        try:
            r = requests.get(f"https://www.amazon.in/dp/{asin}", impersonate="chrome", timeout=30,
                             headers={"Accept-Language": "en-IN,en;q=0.9"})
            last = r
            if r.status_code == 200 and "captcha" not in r.text.lower()[:200000] or r.status_code == 404:
                break
        except Exception as e:  # network error
            last = e
        time.sleep(4)
    return last


def parse(text):
    s = BeautifulSoup(text, "lxml")
    t = s.select_one("#productTitle")
    title = t.get_text(" ", strip=True) if t else None
    price = None
    for sel in PRICE_SEL:
        e = s.select_one(sel)
        if e and e.get_text(strip=True):
            m = re.sub(r"[^\d.]", "", e.get_text(strip=True))
            if m:
                price = int(round(float(m)))
                break
    a = s.select_one("#availability")
    avail = a.get_text(" ", strip=True)[:80] if a else ""
    return title, price, avail


def update_fx(cfg_path, today):
    try:
        from curl_cffi import requests
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=20)
        j = r.json()
        rate = j["rates"]["INR"]
        cfg = json.loads(cfg_path.read_text())
        cfg.update({"usd_inr": round(rate, 2), "usd_inr_date": today, "usd_inr_source": "open.er-api.com (ExchangeRate-API open endpoint)"})
        cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
        print(f"FX: 1 USD = ₹{rate:.2f}")
    except Exception as e:
        print("FX update skipped:", e)


def main():
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    path = ROOT / "data/products.json"
    data = json.loads(path.read_text())
    today = date.today().isoformat()
    ok = blocked = changed = unavailable = 0
    for p in data["products"]:
        if only and p["asin"] not in only:
            continue
        r = fetch(p["asin"])
        if isinstance(r, Exception) or r is None or r.status_code != 200 or "captcha" in r.text.lower()[:200000]:
            blocked += 1
            print(f"KEEP  {p['asin']} fetch failed/blocked ({getattr(r, 'status_code', r)}); last price {p.get('price')} from {p['price_checked']}")
            time.sleep(3)
            continue
        title, price, avail = parse(r.text)
        if not title:
            blocked += 1
            print(f"KEEP  {p['asin']} page has no product title (blocked or removed); last price {p.get('price')} from {p['price_checked']}")
            time.sleep(3)
            continue
        ok += 1
        if "unavailable" in (avail or "").lower():
            price = None  # a stray price on an unavailable page is not a buyable price
        p["availability"] = avail or None
        if p.get("ignore_price"):
            p["price_checked"] = today
            print(f"SKIP  {p['asin']} ignore_price (observed {price})")
        elif price and not in_stock(avail):
            # a price without a recognisable "In stock" availability line can be another seller's/similar-item price: do not trust it
            print(f"KEEP  {p['asin']} price {price} read but availability line is {avail!r}; keeping {p.get('price')} from {p['price_checked']}")
        elif price:
            if price != p.get("price"):
                changed += 1
                print(f"PRICE {p['asin']} {p.get('price')} -> {price}  {p['name'][:50]}")
            p.pop("price_note", None)
            p["price"], p["price_checked"] = price, today
        elif "unavailable" in (avail or "").lower() or not p.get("price"):
            if p.get("price"):
                p["last_price"], p["last_price_date"] = p["price"], p["price_checked"]
                unavailable += 1
                print(f"UNAV  {p['asin']} no price now (was {p['price']}): {avail}")
            p["price"], p["price_checked"] = None, today
            p["price_note"] = ("Currently unavailable on Amazon.in when checked." if "unavailable" in (avail or "").lower()
                               else "No price shown on the Amazon.in page when checked.")
        else:
            print(f"KEEP  {p['asin']} page loaded but no price parsed; keeping {p['price']} from {p['price_checked']}")
        time.sleep(3)
    if ok:
        data["updated"] = today
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(f"Done: {ok} pages read, {blocked} blocked/failed (last good price kept), {changed} price changes, {unavailable} newly unavailable.")
    if "--no-fx" not in sys.argv:
        update_fx(ROOT / "data/config.json", today)
    if only is None and ok == 0:
        print("WARNING: no page could be read; data unchanged.")


if __name__ == "__main__":
    main()
