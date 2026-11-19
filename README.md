# GTA 6 Setup Builder

Free static site (GitHub Pages) with a budget-based GTA 6 gaming setup builder for console players in India, four SEO buying guides and Amazon.in affiliate links. Not affiliated with Rockstar Games.

Live: https://gta6-setup-five.vercel.app/ (fallback: https://ajaynallavelli.github.io/gta6-setup/)

## Layout

```
data/products.json       # products: ASIN, category, platforms, rank, price (INR, as shown on amazon.in), price_checked date, why
data/config.json         # amazon_tag (Associates tracking ID; empty = links carry no ?tag=), USD/INR rate for the optional USD toggle
data/facts.json          # GTA 6 platform / release-date facts with official sources and the date checked
content/guides/*.json    # the 4 buying guides (picks reference ASINs; prices come from products.json)
scripts/build.py         # Jinja2 static generator -> dist/ (pages, sitemap.xml, robots.txt, JSON-LD)
scripts/refresh_prices.py# polite Amazon.in price re-check (curl_cffi); keeps last good price if blocked
scripts/check_links.py   # internal link + Amazon link (rel, tag) checker
scripts/seed_products.py # one-time seed that created products.json (do not re-run)
static/builder.js        # client-side recommendation logic (reads data/products.json)
.github/workflows/deploy.yml  # daily: refresh prices -> commit -> build -> deploy to Pages
```

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./run.sh build     # build dist/ and check links
./run.sh prices    # refresh prices from Amazon.in
./run.sh serve     # http://localhost:8788/gta6-setup/ (serve mirrors the GitHub Pages subpath; Vercel serves from root, see Deploy)
```

## Affiliate tag

Every Amazon link is built by one function (`scripts/common.py: amazon_url`, mirrored in `static/builder.js`) as `https://www.amazon.in/dp/<ASIN>?tag=<amazon_tag>`. Set `"amazon_tag"` in `data/config.json` once the Associates account exists; with an empty tag the links still work, just untracked. Links carry `rel="sponsored nofollow noopener"` and an "Affiliate link" label; the footer and a top bar carry the Amazon Associates disclosure.

## Prices

`refresh_prices.py` only updates a price from a product page that loaded (HTTP 200, no captcha, product title present). Otherwise the last good price and its date are kept. If the page loads but shows no price / "currently unavailable", the product shows "Check price" and the previous price is kept in `last_price`. Products flagged `ignore_price` (implausible third-party-only listings) never get a price.

## Analytics

GA4 uses the same measurement ID as GTMStack Tracker (`site.json: ga4_measurement_id`); `affiliate_click` events carry `site=gta6-setup` and `page_path`, so they can be filtered from GTMStack's.

## Deploy

- **Vercel (primary, https://gta6-setup-five.vercel.app):** `vercel.json` builds with `scripts/build.py` into `dist/` and serves from the domain root. The canonical URL comes from Vercel's `VERCEL_PROJECT_PRODUCTION_URL`. Currently deployed as a bootstrap deployment whose build downloads `main` from GitHub, so redeploy (Vercel create_deployment / redeploy) to publish new commits until the Vercel GitHub login connection is added for auto-deploy.
- **GitHub Pages (fallback):** the workflow builds with `SITE_BASE_URL=https://ajaynallavelli.github.io/gta6-setup` so links carry the `/gta6-setup/` subpath.
- Any build can override the base with the `SITE_BASE_URL` env var, e.g. `SITE_BASE_URL=https://example.com ./run.sh build`.
