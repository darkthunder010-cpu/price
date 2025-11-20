# scripts/scrape_all.py
import time
from scraper import scrape_price
import db
import sqlite3
from datetime import datetime

# adjust these to control politeness and retry behavior
DELAY_BETWEEN_REQUESTS = 3.0  # seconds between requests
RETRY_COUNT = 2

def safe_scrape(url):
    for attempt in range(RETRY_COUNT):
        try:
            return scrape_price(url)
        except Exception as e:
            print(f"Scrape error (attempt {attempt+1}) for {url}: {e}")
            time.sleep(2 + attempt*2)
    return {"url": url, "price": None, "timestamp": datetime.utcnow().isoformat(), "error": "failed"}

def scrape_all(path_db="prices.db"):
    db.init_db(path_db)
    prods = db.list_products(path_db)
    print(f"Found {len(prods)} products to scrape.")
    for p in prods:
        url = p["url"]
        print(f"Scraping {p['id']} {url}")
        r = safe_scrape(url)
        if r.get("price") is not None:
            try:
                db.add_price(p["id"], float(r["price"]), ts=r.get("timestamp"), path=path_db)
                print(f"Stored price {r['price']} for product {p['id']}")
            except Exception as e:
                print("DB insert error:", e)
        else:
            print("No price found:", r.get("error"))
        time.sleep(DELAY_BETWEEN_REQUESTS)

if __name__ == "__main__":
    scrape_all()
