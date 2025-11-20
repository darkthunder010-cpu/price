# Simple Price History & Prediction (starter)

A compact demo that tracks product prices and makes a simple linear-trend prediction.

## Tech
- Python (3.10+)
- Streamlit (UI)
- SQLite (storage)
- BeautifulSoup (scraping)
- scikit-learn (linear regression)
- Plotly (charts)

## Quick start
1. python -m venv .venv && source .venv/bin/activate
2. pip install -r requirements.txt
3. python -c "import db; db.init_db()"
4. streamlit run app.py

## Notes
- This is a demo. For robust production scraping use official APIs (Keepa, SerpApi) where possible.


