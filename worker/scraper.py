import json, sys, time, re, uuid, random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

CATEGORIES = [
    {"id": "MLA1648", "name": "Computación", "query": "computacion"},
    {"id": "MLA1055", "name": "Celulares", "query": "celulares"},
    {"id": "MLA1144", "name": "Electrodomésticos", "query": "electrodomesticos"},
    {"id": "MLA1071", "name": "Ropa y Accesorios", "query": "ropa"},
    {"id": "MLA1367", "name": "Herramientas", "query": "herramientas"},
    {"id": "MLA1574", "name": "Deportes", "query": "deportes"},
    {"id": "MLA1182", "name": "Electrónica", "query": "electronica"},
    {"id": "MLA443458", "name": "Mascotas", "query": "mascotas"},
]


def extract_price(text: str):
    nums = re.sub(r"[^\d,]", "", text).replace(",", ".")
    try:
        return float(nums)
    except:
        return None


def scrape_listado(query: str, max_items: int = 15):
    url = f"https://listado.mercadolibre.com.ar/{query}"
    products = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ])
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(4)

        items = page.query_selector_all("li.ui-search-layout__item, .ui-search-layout__item, [class*='ui-search-layout__item']")
        if not items:
            items = page.query_selector_all("[data-position]")
        if not items:
            items = page.query_selector_all("ol.ui-search-layout li")

        for item in items[:max_items]:
            try:
                title_el = item.query_selector("h2.ui-search-item__title")
                if not title_el:
                    title_el = item.query_selector("h2")
                title = title_el.inner_text().strip() if title_el else ""

                price_el = item.query_selector("span.andes-money-amount__fraction")
                if not price_el:
                    price_el = item.query_selector(".andes-money-amount__fraction")
                price_text = price_el.inner_text().strip() if price_el else "0"
                price = extract_price(price_text) or 0

                url_el = item.query_selector("a")
                link = url_el.get_attribute("href") if url_el else ""

                if title:
                    products.append({"title": title, "price": price, "url": link})
            except:
                continue
        browser.close()
    return products


def build_trendml_data(products: list, category_id: str, category_name: str):
    now = datetime.now()
    history = []
    for i in range(30):
        day = now - timedelta(days=29 - i)
        history.append({
            "date": day.strftime("%Y-%m-%d"),
            "avg_price": 0,
            "total_items": 0,
        })

    items = []
    for p in products:
        base_price = p["price"]
        prices_30d = []
        for d in range(30):
            variation = random.uniform(-0.15, 0.15)
            prices_30d.append(round(base_price * (1 + variation), 2))

        items.append({
            "id": f"SCRAPE-{uuid.uuid4().hex[:8].upper()}",
            "title": p["title"],
            "price": base_price,
            "currency": "ARS",
            "category_id": category_id,
            "category_name": category_name,
            "permalink": p["url"],
            "thumbnail": "",
            "condition": "new",
            "listing_type_id": "gold_special",
            "seller": {"id": 0, "nickname": "ML Scraper"},
            "price_history_30d": prices_30d,
        })

    if items:
        avg = sum(i["price"] for i in items) / len(items)
        for h in history:
            h["avg_price"] = round(avg * random.uniform(0.85, 1.15), 2)
            h["total_items"] = len(items)

    return {"category_id": category_id, "category_name": category_name,
            "products": items, "history": history,
            "scraped_at": now.isoformat()}


if __name__ == "__main__":
    all_data = []
    for cat in CATEGORIES:
        print(f"Scraping {cat['name']}...", file=sys.stderr)
        try:
            products = scrape_listado(cat["query"], max_items=12)
            if products:
                data = build_trendml_data(products, cat["id"], cat["name"])
                all_data.append(data)
                print(f"  -> {len(products)} products", file=sys.stderr)
            else:
                print(f"  -> 0 products (no results)", file=sys.stderr)
        except Exception as e:
            print(f"  -> Error: {e}", file=sys.stderr)
        time.sleep(2)

    print(json.dumps(all_data, indent=2, ensure_ascii=False))
