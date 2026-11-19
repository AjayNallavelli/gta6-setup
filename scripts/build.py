#!/usr/bin/env python3
"""Static site generator: data/*.json + content/guides/*.json + templates/ -> dist/."""
import html, json, re, shutil, sys
from datetime import date
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load, amazon_url, inr

OUT = ROOT / "dist"
CATS = [("console", "Consoles"), ("tv", "TVs"), ("monitor", "Monitors"), ("headset", "Headsets"),
        ("controller", "Controllers"), ("storage", "Storage"), ("cable", "HDMI cables"), ("charger", "Chargers")]
PLAT = {"ps5": "PS5", "ps5pro": "PS5 Pro", "xsx": "Xbox Series X", "xss": "Xbox Series S"}


def main():
    site, cfg, facts = load("site.json"), load("data/config.json"), load("data/facts.json")
    products = load("data/products.json")
    prods = products["products"]
    by_asin = {p["asin"]: p for p in prods}
    tag = cfg.get("amazon_tag", "")
    for p in prods:
        p["url"] = amazon_url(p["asin"], tag)
    base = urlbase(site)
    guides = [json.loads(f.read_text().replace("@BASE@", base)) for f in sorted((ROOT / "content/guides").glob("*.json"))]
    guides.sort(key=lambda g: g.get("order", 99))
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html", "xml"]))
    env.filters["inr"] = inr
    env.filters["tojson_safe"] = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    env.globals.update(site=site, base=base, facts=facts, tag=tag, cats=CATS, plat=PLAT, by_asin=by_asin,
                       products_meta=products, guides=guides, today=date.today().isoformat())
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    pages = []

    def render(tpl, path, title, description, lastmod=None, sitemap=True, ld=None, **ctx):
        dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(env.get_template(tpl).render(path=path, title=title, description=description, ld=ld or [], **ctx))
        if sitemap:
            pages.append((path, lastmod or products["updated"]))

    n_priced = sum(1 for p in prods if p.get("price"))
    render("index.html", "/", "GTA 6 Setup Builder: console, TV or monitor, headset and storage for your budget (India)",
           "Enter your budget in INR and your console and get a GTA 6 setup: display, headset, controller, storage and cable, with prices checked on Amazon.in.",
           n_priced=n_priced, n_products=len(prods),
           ld=[{"@context": "https://schema.org", "@type": "WebApplication", "name": site["name"],
                "url": site["base_url"] + "/", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any",
                "description": "Budget-based gaming setup builder for Grand Theft Auto VI on consoles, with prices checked on Amazon.in."}])
    render("guides_index.html", "/guides/", "GTA 6 buying guides for India: TV, headset, monitor, PS5 vs PS5 Pro",
           "Four buying guides for a Grand Theft Auto VI setup in India, with prices checked on Amazon.in and no fake reviews.")
    for g in guides:
        picks = [{**by_asin[x["asin"]], "role": x.get("role", ""), "verdict": x.get("verdict", "")} for x in g.get("picks", [])]
        url = f"{site['base_url']}/guides/{g['slug']}/"
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in g["faq"]]}
        art_ld = {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "description": g["description"],
                  "dateModified": g["updated"], "datePublished": g.get("published", g["updated"]), "mainEntityOfPage": url,
                  "author": {"@type": "Organization", "name": site["name"]}, "publisher": {"@type": "Organization", "name": site["name"]}}
        render("guide.html", f"/guides/{g['slug']}/", g["title"], g["description"], lastmod=g["updated"], g=g, picks=picks, ld=[faq_ld, art_ld])
    render("platforms.html", "/gta-6-platforms-release-date/", "GTA 6 platforms and release date: PS5, PS5 Pro, Xbox Series X|S (checked " + facts["checked"] + ")",
           "What Rockstar and PlayStation officially say about Grand Theft Auto VI platforms and release date, with sources and the date we checked.",
           lastmod=facts["checked"])
    render("products.html", "/products/", "All products in the GTA 6 Setup Builder (Amazon.in prices, dated)",
           "Every product the builder can recommend, with ASIN, the price shown on Amazon.in and the date it was checked.")
    render("about.html", "/about/", "About, affiliate disclosure and how prices are checked",
           "We are an independent site, not affiliated with Rockstar Games, Take-Two, Sony, Microsoft or Amazon. As an Amazon Associate we earn from qualifying purchases.",
           lastmod=products["updated"])
    (OUT / "404.html").write_text(env.get_template("404.html").render(path="/404.html", title="Page not found", description="Page not found", ld=[]))
    # static + data
    shutil.copytree(ROOT / "static", OUT / "static")
    (OUT / "data").mkdir()
    for f in ("products.json", "config.json", "facts.json"):
        shutil.copy(ROOT / "data" / f, OUT / "data" / f)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p, lm in pages:
        sm.append(f"  <url><loc>{html.escape(site['base_url'] + p)}</loc><lastmod>{lm}</lastmod></url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {site['base_url']}/sitemap.xml\n")
    (OUT / ".nojekyll").write_text("")
    print(f"Built {len(pages)} sitemap pages, {len(prods)} products ({n_priced} with a price) -> {OUT}")


def urlbase(site):
    from urllib.parse import urlparse
    return urlparse(site["base_url"]).path.rstrip("/")


if __name__ == "__main__":
    main()
