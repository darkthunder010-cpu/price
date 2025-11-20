# scripts/bulk_add.py
import csv
import sys
import db

def bulk_add(csv_path):
    db.init_db()
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row: continue
            # handle lines like: url,title or just url
            url = row[0].strip()
            title = row[1].strip() if len(row) > 1 else None
            if url:
                prod = db.add_product(url, title=title)
                print("Added:", prod)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/bulk_add.py products.csv")
    else:
        bulk_add(sys.argv[1])
