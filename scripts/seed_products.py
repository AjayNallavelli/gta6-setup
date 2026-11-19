#!/usr/bin/env python3
"""ONE-TIME seed: curated product metadata + the first verified Amazon.in page reads -> data/products.json.
Do not re-run after launch (it overwrites); scripts/refresh_prices.py maintains prices and dates."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
CHECKED = "2026-11-19"
ALL = ["ps5", "ps5pro", "xsx", "xss"]
PS = ["ps5", "ps5pro"]
XB = ["xsx", "xss"]
# asin, category, platforms, rank, short name, why (only claims taken from the Amazon.in listing text or well-known official facts), extras
C = [
 # consoles (no price read: unavailable / no price shown / third-party only)
 ("B0GNMKL3VP","console",["ps5"],1,"Sony PlayStation 5 Slim console","Sony's current PS5 (Slim). GTA 6 is listed for PS5 on Rockstar's and PlayStation's official pages.",{}),
 ("B09NPR1GLZ","console",["xss"],1,"Xbox Series S 512GB all-digital console","The cheapest way into Xbox Series X|S, which Rockstar lists for GTA 6. All-digital, 512GB internal storage.",{}),
 ("B08H75RTZ8","console",["xsx"],1,"Xbox Series X 1TB console","Xbox Series X|S is a listed GTA 6 platform. Amazon.in only showed a third-party seller at an abnormal price when checked.",{"ignore_price":True,"price_note":"Only a third-party seller (₹2,10,890 when checked), far above normal retail. Check Xbox.com or an authorised retailer."}),
 # TVs
 ("B0F6YVKDR2","tv",ALL,2,"Xiaomi 55-inch X 4K Google TV (L55MB-AIN)","Entry 55-inch 4K with Dolby Vision; listing mentions a 120Hz game booster (DLG) but a 60Hz native panel, and 3 HDMI ports.",{"size":"55"}),
 ("B0FJLSNZBW","tv",ALL,3,"Hisense 55E75Q 55-inch 4K QLED","Listing shows 3 HDMI 2.1 ports with ALLM and VRR on a QLED panel. Refresh rate is listed as 60Hz, so 4K120 is not advertised.",{"size":"55"}),
 ("B0GTZ8WM5W","tv",ALL,3,"LG 55NU870BPLA 55-inch NU87 4K","Listing shows ALLM and eARC on HDMI and LG's α7 processor. Native 60Hz, so no 4K120.",{"size":"55"}),
 ("B0H2BWX52Y","tv",ALL,4,"Xiaomi 55-inch FX QD-Mini LED 4K (L55MC-FSMIN)","Quantum-dot Mini LED with full-array local dimming and HDR10+/Dolby Vision, the best contrast of the 55-inch picks here. 60Hz native (120Hz via DLG).",{"size":"55"}),
 ("B0F7X5FC43","tv",ALL,4,"Sony BRAVIA 2M2 55-inch K-55S25BM2","Sony's 55-inch with a Game Menu and ALLM/eARC (HDMI 2.1 compatible) per the listing. 60Hz panel; you pay for the brand and processing.",{"size":"55"}),
 ("B0GYD83B13","tv",ALL,5,"iFFALCON 65-inch 65U75 4K Google TV","Largest screen here at 65 inches; listing says 120Hz refresh (DLG 288Hz) with VRR and a Game Master mode.",{"size":"65"}),
 ("B0F4WZWKSL","tv",ALL,6,"Hisense 55E7Q 55-inch 4K QLED (144Hz)","Best match for console gaming in this list: listing shows 3 HDMI 2.1 ports, a 144Hz Game Mode Pro and Dolby Vision on a QLED panel.",{"size":"55"}),
 # monitors
 ("B0DQP36N7T","monitor",ALL,1,"MSI MAG 255F E20 24.5-inch FHD 200Hz","Cheapest option here: Rapid IPS, 200Hz, HDMI 2.0b input listed at FHD@200Hz. Full HD only.",{}),
 ("B0D4YPL67T","monitor",ALL,2,"LG 24GS60F 24-inch FHD 180Hz","23.8-inch IPS, 180Hz, 1ms, HDR10 and 99% sRGB per the listing.",{}),
 ("B0H69FXJC8","monitor",ALL,2,"Lenovo LOQ 24-10 24-inch FHD 200Hz","IPS, 200Hz, 0.5ms (MPRT) and 99% sRGB per the listing. Full HD.",{}),
 ("B0HFSLVGBK","monitor",ALL,2,"LG 27G411B 27-inch FHD 144Hz","27-inch IPS, 144Hz, 1ms MBR with a Dynamic Action Sync mode to cut input lag, per the listing. Full HD stretched over 27 inches.",{}),
 ("B0H696XFPH","monitor",ALL,4,"Lenovo LOQ 27Q-10 27-inch QHD 180Hz","QHD (2560x1440) IPS, 180Hz, and the listing shows 2 HDMI 2.1 ports. Sharper than Full HD at a modest price.",{}),
 ("B08B7VX691","monitor",ALL,4,"Acer Nitro VG270U Z2 27-inch QHD 275Hz","QHD IPS with HDMI 2.1 and DisplayPort 1.4 per the listing, 90% DCI-P3 and HDR10.",{}),
 ("B0DCBDVNLD","monitor",ALL,3,"LG 32GS60QC 32-inch curved QHD 180Hz","32-inch curved VA panel at QHD, 180Hz, with 2 HDMI ports per the listing. Biggest desk screen under ₹20,000 here.",{}),
 ("B0GF2QG5K3","monitor",ALL,3,"Samsung Odyssey G5 27-inch QHD 180Hz","QHD Fast IPS, 180Hz, HDR10 and a 3-year manufacturer warranty per the listing. HDMI 2.0 only.",{}),
 ("B0H7VRS6S9","monitor",ALL,6,"Acer Nitro XV270K V2 27-inch 4K 144Hz","True 4K IPS with 2 HDMI 2.1 ports per the listing: the monitor to pick for 4K at high refresh from a console.",{}),
 # headsets
 ("B0F18JLKZW","headset",["ps5"],1,"PowerA LucidSound LS10P Gen 2 (wired)","Wired PS5/PS4/PC headset with 50mm drivers, flip-to-mute mic and Tempest 3D Audio support per the listing. Cheapest here.",{"wireless":False}),
 ("B086PKMZ21","headset",ALL,3,"Razer BlackShark V2 X (wired, 3.5mm)","3.5mm wired, 50mm drivers, memory-foam cushions; the listing says multi-platform (PC/PS/Xbox/Switch/Mobile).",{"wireless":False}),
 ("B07QB2Y272","headset",ALL,3,"Logitech G431 (wired, USB + 3.5mm)","50mm drivers and a flip-to-mute mic; the listing says consoles connect with the 3.5mm cable.",{"wireless":False}),
 ("B0DXQ8X9GT","headset",PS,3,"HyperX Cloud Jet dual wireless (2.4GHz + Bluetooth)","Wireless under ₹5,000: 2.4GHz USB-A dongle plus Bluetooth 5.2, swivel-to-mute mic; the title lists PS5.",{"wireless":True}),
 ("B00SAYCXWG","headset",PS,4,"HyperX Cloud II (wired)","Long-running wired HyperX with virtual 7.1 surround and memory foam; the title lists PC and PS5/PS4.",{"wireless":False}),
 ("B0C3BV19Q3","headset",ALL,5,"HyperX Cloud III (wired, USB-C/USB-A/3.5mm)","Angled 53mm drivers and a 10mm mic; the title lists PS5 and Xbox Series X|S.",{"wireless":False}),
 ("B0B4RNCRNS","headset",PS,5,"Logitech G535 Lightspeed wireless","Wireless USB dongle, 236g, 33 hours battery per the listing; compatible with PS4/PS5.",{"wireless":True}),
 ("B0CNPD3NSK","headset",PS,6,"Sony INZONE H5 wireless","Sony-made wireless headset with 360 Spatial Sound, 28-hour battery and 2.4GHz dongle; the listing says it works with PS5.",{"wireless":True}),
 # controllers
 ("B0HN49PKLM","controller",PS,1,"EvoFox Play V PS5 controller (Hall effect sticks)","Third-party PS5 pad with drift-resistant Hall-effect sticks and a 10-hour battery per the listing. A cheap second pad.",{}),
 ("B0HGGC5XGQ","controller",PS,3,"Sony DualSense Icon Blue (special edition)","Sony's own PS5 controller with haptics and adaptive triggers, in a special-edition colour (the standard DualSense listing was unavailable when checked).",{}),
 ("B0BMPLHLZ9","controller",PS,5,"Sony DualSense Edge","Remappable inputs, swappable back buttons and changeable stick caps per the listing. Pricey; for players who want the customisation.",{}),
 ("B0FFGQ5KW8","controller",XB,3,"Xbox Wireless Controller, Carbon Black","The official Xbox controller for Series X|S: textured grips and a hybrid D-pad per the listing.",{}),
 ("B0F2NCQYTX","controller",XB,3,"Xbox Wireless Controller, Robot White","Same official Xbox controller in white.",{}),
 # storage
 ("B0DV3C5HQH","storage",PS,2,"Crucial P310 1TB PCIe 4.0 NVMe SSD with heatsink","M.2 2280 PCIe 4.0 NVMe, up to 7,100MB/s read, with heatsink per the listing: the form factor and heatsink the PS5's M.2 slot needs. Check Sony's M.2 requirements before buying.",{}),
 ("B0DV32WGWM","storage",PS,3,"Crucial P310 2TB PCIe 4.0 NVMe SSD with heatsink","Same drive in 2TB: room for a few more 100GB+ games. Check Sony's M.2 requirements.",{}),
 ("B0C47ZX1WB","storage",PS,4,"WD_BLACK SN850P 2TB for PS5","Listed as an officially licensed M.2 SSD for PS5 with a PS5-specific heatsink, up to 7,300MB/s read. The safest, most expensive choice.",{}),
 ("B0C44XVWCH","storage",XB,3,"WD_BLACK C50 1TB expansion card for Xbox","Xbox Series X|S games must run from internal SSD or an expansion card; the listing says the C50 matches internal storage performance. No price shown when checked.",{}),
 # cables
 ("B07VSG5SXZ","cable",ALL,1,"Zebronics HDMI 2.1 cable, 2m","Listing says 48Gbps with 4K at 120Hz support. Cheapest HDMI 2.1 cable here.",{}),
 ("B08HRG2MB5","cable",ALL,2,"Honeywell HDMI 2.1 cable, 2m","Listing says 48Gbps, 4K@120Hz, ALLM, eARC.",{}),
 ("B0CFFFSFFN","cable",ALL,3,"UGREEN 8K HDMI 2.1 cable, 2m","Listing says it carries the HDMI 2.1 Ultra High Speed certification at 48Gbps, with eARC.",{}),
 # chargers
 ("B0F8MZV8PK","charger",PS,1,"Zebronics PS5C dual dock","Charges two DualSense or DualSense Edge controllers at once via pogo pins, per the listing.",{}),
 ("B0C8RGL1JG","charger",PS,2,"PowerA Solo charging station for DualSense","PlayStation-licensed single dock with a weighted base, per the listing.",{}),
 ("B0DP6N7ZCF","charger",PS,3,"PowerA Twin charging station for DualSense","PlayStation-licensed dock for two controllers, AC adaptor included, per the listing.",{}),
 ("B08HLWNLDH","charger",XB,2,"Xbox Play and Charge Kit V2 (USB-C)","Rechargeable battery pack and USB-C cable for the Xbox controller, per the listing.",{}),
]
pages = {}
for f in ("/tmp/p2.txt", "/tmp/p3.txt", "/tmp/p4.txt", "/tmp/p5.txt", "/tmp/p0.txt"):
    try:
        for l in open(f):
            try: d = json.loads(l)
            except Exception: continue
            pages[d["asin"]] = d
    except FileNotFoundError:
        pass
out = []
for asin, cat, plats, rank, name, why, ex in C:
    d = pages.get(asin)
    if not d: print("MISSING page read", asin); continue
    price = None
    if d.get("price") and "unavailable" not in (d.get("avail") or "").lower():
        price = int(round(float(re.sub(r"[^\d.]", "", d["price"]))))
    avail = (d.get("avail") or "").strip() or None
    p = {"asin": asin, "name": name, "amazon_title": d["title"], "category": cat, "platforms": plats, "rank": rank, "why": why,
         "price": price, "price_checked": CHECKED, "availability": avail, "source": f"https://www.amazon.in/dp/{asin}"}
    if cat == "headset": p["wireless"] = ex.get("wireless", False)
    if ex.get("size"): p["size_inch"] = ex["size"]
    if ex.get("ignore_price"):
        p["price"] = None; p["ignore_price"] = True
    if p["price"] is None:
        p["price_note"] = ex.get("price_note") or ("Currently unavailable on Amazon.in when checked." if avail and "unavailable" in avail.lower() else "No price shown on the Amazon.in page when checked.")
    out.append(p)
(ROOT / "data/products.json").write_text(json.dumps({"updated": CHECKED, "currency": "INR", "source": "amazon.in product pages", "products": out}, indent=1, ensure_ascii=False) + "\n")
print(len(out), "products;", sum(1 for p in out if p["price"]), "with price")
