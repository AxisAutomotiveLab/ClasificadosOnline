import asyncio
import json
import re
import os
from datetime import datetime, timezone
from playwright.async_api import async_playwright

DEALERS = [
    {"id": "34602", "name": "Autocentro Mas",       "location": "San Juan - Río Piedras", "is_own": True},
    {"id": "1158",  "name": "CAGUAX Auto Sales",    "location": "Caguas",                 "is_own": False},
    {"id": "5439",  "name": "PITA Auto Sales",       "location": "Carolina",               "is_own": False},
    {"id": "4161",  "name": "Villa Victoria",        "location": "Caguas",                 "is_own": False},
    {"id": "568",   "name": "Eurojapon",             "location": "Bayamón",                "is_own": False},
    {"id": "6160",  "name": "Autogermana Pre-Owned", "location": "San Juan - Hato Rey",    "is_own": False},
    {"id": "35021", "name": "CARPRO",                "location": "San Juan - Río Piedras", "is_own": False},
    {"id": "27205", "name": "Stuttgart Auto",        "location": "Caguas",                 "is_own": False},
]

BASE_URL = "https://www.clasificadosonline.com/PartnersListingTranspID.asp?ID={id}&offset={offset}"

def parse_price(desc):
    if not desc:
        return None
    m = re.match(r'(\d+)', desc.strip())
    if m:
        val = int(m.group(1))
        return val if val > 1000 else None
    return None

async def scrape_dealer(page, dealer):
    vehicles = []
    offset = 0
    total = None

    while True:
        url = BASE_URL.format(id=dealer["id"], offset=offset)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1500)
        except Exception as e:
            print(f"  Error loading {url}: {e}")
            break

        if total is None:
            total_text = await page.text_content("span.Tahoma16BrownNound") or ""
            m = re.search(r'de\s+(\d+)', total_text)
            total = int(m.group(1)) if m else 0
            print(f"  {dealer['name']}: {total} total units")

        items = await page.query_selector_all("span[itemtype='https://schema.org/product']")

        for item in items:
            name_el    = await item.query_selector("meta[itemprop='name']")
            mfg_el     = await item.query_selector("meta[itemprop='manufacturer']")
            model_el   = await item.query_selector("meta[itemprop='model']")
            desc_el    = await item.query_selector("meta[itemprop='description']")
            img_el     = await item.query_selector("meta[itemprop='image']")

            name  = await name_el.get_attribute("content")  if name_el  else ""
            mfg   = await mfg_el.get_attribute("content")   if mfg_el   else ""
            model = await model_el.get_attribute("content") if model_el else ""
            desc  = await desc_el.get_attribute("content")  if desc_el  else ""
            img   = await img_el.get_attribute("content")   if img_el   else ""

            year_m = re.search(r'\b(19|20)\d{2}\b', name)
            year = int(year_m.group(0)) if year_m else None

            price = parse_price(desc)

            vehicles.append({
                "name":         name.strip(),
                "manufacturer": mfg.strip(),
                "model":        model.strip(),
                "year":         year,
                "price":        price,
                "image":        img.strip(),
            })

        if total and offset + 50 < total:
            offset += 50
            await page.wait_for_timeout(1200)
        else:
            break

    prices = [v["price"] for v in vehicles if v["price"]]
    return {
        "id":        dealer["id"],
        "name":      dealer["name"],
        "location":  dealer["location"],
        "is_own":    dealer["is_own"],
        "total":     total or len(vehicles),
        "vehicles":  vehicles,
        "price_min": min(prices) if prices else None,
        "price_max": max(prices) if prices else None,
        "price_avg": round(sum(prices) / len(prices)) if prices else None,
        "prices_hidden": len(prices) == 0,
        "url": f"https://www.clasificadosonline.com/PartnersListingTranspID.asp?ID={dealer['id']}",
    }

async def main():
    print(f"Starting scrape at {datetime.now(timezone.utc).isoformat()}")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        for dealer in DEALERS:
            print(f"Scraping {dealer['name']}...")
            try:
                data = await scrape_dealer(page, dealer)
                results.append(data)
                print(f"  Done: {len(data['vehicles'])} vehicles extracted")
            except Exception as e:
                print(f"  FAILED: {e}")
                results.append({
                    "id": dealer["id"], "name": dealer["name"],
                    "location": dealer["location"], "is_own": dealer["is_own"],
                    "total": 0, "vehicles": [], "error": str(e),
                    "price_min": None, "price_max": None, "price_avg": None,
                    "prices_hidden": True,
                    "url": f"https://www.clasificadosonline.com/PartnersListingTranspID.asp?ID={dealer['id']}",
                })
            await asyncio.sleep(2)

        await browser.close()

    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%d %b %Y, %I:%M %p UTC"),
        "updated_at_iso": datetime.now(timezone.utc).isoformat(),
        "dealers": results,
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nSaved docs/data.json")
    print(f"Total dealers: {len(results)}")
    total_v = sum(d['total'] for d in results)
    print(f"Total vehicles: {total_v}")

if __name__ == "__main__":
    asyncio.run(main())
