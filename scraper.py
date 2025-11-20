# scraper.py
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "price-history-demo/0.1 (+https://example.com)"
}

def extract_price_from_text(text):
    m = re.search(r'([₹$€]\s?[0-9][0-9,\.]*)', text)
    if m:
        s = m.group(1)
        s = re.sub(r'[₹$€\s,]', '', s)
        try:
            return float(s)
        except:
            return None
    m2 = re.search(r'([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)', text)
    if m2:
        s = m2.group(1).replace(',', '')
        try:
            return float(s)
        except:
            return None
    return None

def scrape_price(url, session=None, timeout=10):
    s = session or requests.Session()
    try:
        resp = s.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        return {"url": url, "price": None, "timestamp": datetime.utcnow().isoformat(), "error": str(e)}
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    # 1) try JSON-LD price (common)
    scripts = soup.find_all("script", type="application/ld+json")
    for sc in scripts:
        try:
            import json
            data = json.loads(sc.string or "{}")
            if isinstance(data, list):
                for d in data:
                    price = (d.get("offers") or {}).get("price")
                    if price:
                        return {"url": url, "price": float(price), "timestamp": datetime.utcnow().isoformat(), "title": d.get("name")}
            elif isinstance(data, dict):
                offers = data.get("offers")
                if isinstance(offers, dict):
                    price = offers.get("price")
                    if price:
                        return {"url": url, "price": float(price), "timestamp": datetime.utcnow().isoformat(), "title": data.get("name")}
        except Exception:
            pass

    meta_price = soup.find("meta", {"property": "product:price:amount"}) or soup.find("meta", {"itemprop": "price"})
    if meta_price and meta_price.get("content"):
        try:
            return {"url": url, "price": float(meta_price["content"]), "timestamp": datetime.utcnow().isoformat(), "title": soup.title.string.strip() if soup.title else None}
        except:
            pass

    selectors = ['[id*="price"]', '[class*="price"]', '[class*="Price"]']
    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            p = extract_price_from_text(el.get_text(" ", strip=True))
            if p is not None:
                return {"url": url, "price": p, "timestamp": datetime.utcnow().isoformat(), "title": soup.title.string.strip() if soup.title else None}

    p = extract_price_from_text(soup.get_text(" ", strip=True)[:6000])
    if p is not None:
        return {"url": url, "price": p, "timestamp": datetime.utcnow().isoformat(), "title": soup.title.string.strip() if soup.title else None}

    return {"url": url, "price": None, "timestamp": datetime.utcnow().isoformat(), "title": soup.title.string.strip() if soup.title else None}
