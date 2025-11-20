# app.py
import streamlit as st
from scraper import scrape_price
import db
import pandas as pd
from datetime import datetime
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Price History (Simple)", layout="wide")
db.init_db()

st.title("Price History — Simple Version")

# Add product form
with st.form("add_product"):
    url = st.text_input("Product URL")
    submit = st.form_submit_button("Add product")
    if submit and url:
        res = scrape_price(url)
        prod = db.add_product(url, title=res.get("title") or url)
        if res.get("price") is not None:
            db.add_price(prod["id"], res["price"], ts=res["timestamp"])
        st.success("Product added (and price recorded if found).")

products = db.list_products()
if not products:
    st.info("No products yet. Add a product URL above.")
else:
    cols = st.columns([3,1,1])
    with cols[0]:
        chosen = st.selectbox("Select product", options=[p["url"] for p in products], format_func=lambda x: x)
    product = next(p for p in products if p["url"]==chosen)
    hist = db.get_price_history(product["id"])
    if len(hist) == 0:
        st.warning("No price history yet. Run the scraper (see instructions).")
    else:
        df = pd.DataFrame(hist)
        df['ts'] = pd.to_datetime(df['ts'])
        df = df.sort_values('ts')
        st.subheader(product.get("title") or product["url"])
        st.write(f"Last recorded price: **{df['price'].iloc[-1]}** at {df['ts'].iloc[-1].isoformat()}")
        fig = px.line(df, x='ts', y='price', markers=True, title="Price history")
        st.plotly_chart(fig, use_container_width=True)

        if len(df) >= 3:
            df = df.reset_index(drop=True)
            x = (df['ts'] - df['ts'].min()).dt.total_seconds().values.reshape(-1,1) / (3600*24)
            y = df['price'].values
            model = LinearRegression()
            model.fit(x, y)
            future_days = np.array([ (df['ts'].max() - df['ts'].min()).total_seconds() / (3600*24) + d for d in range(1,8) ]).reshape(-1,1)
            preds = model.predict(future_days)
            fut_df = pd.DataFrame({
                'ts': [df['ts'].max() + pd.Timedelta(days=int(d)) for d in range(1,8)],
                'pred': preds
            })
            fig2 = px.line(title="Price + 7-day linear trend")
            fig2.add_scatter(x=df['ts'], y=df['price'], mode='lines+markers', name='actual')
            fig2.add_scatter(x=fut_df['ts'], y=fut_df['pred'], mode='lines+markers', name='predicted')
            st.plotly_chart(fig2, use_container_width=True)

            last_price = float(df['price'].iloc[-1])
            next_pred = float(preds[0])
            if next_pred < last_price * 0.98:
                st.success(f"Prediction: price likely to **decrease** soon (pred {next_pred:.2f} vs last {last_price:.2f}). Consider waiting.")
            else:
                st.info(f"Prediction: no significant drop predicted (pred {next_pred:.2f} vs last {last_price:.2f}).")
        else:
            st.info("Need at least 3 data points for a linear trend prediction. Run scraper periodically.")

st.sidebar.header("Maintenance")
if st.sidebar.button("Scrape all products now"):
    prods = db.list_products()
    with st.spinner("Scraping..."):
        for p in prods:
            r = scrape_price(p["url"])
            if r.get("price") is not None:
                db.add_price(p["id"], r["price"], ts=r["timestamp"])
    st.sidebar.success("Scrape complete. Reload main page to see results.")
