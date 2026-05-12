from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import COMMODITIES, ALERT_THRESHOLD_PCT

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

st.set_page_config(
    page_title="Grain Futures Price Forecaster",
    page_icon="🌾",
    layout="wide",
)

@st.cache_data(ttl=3600)
def load_data():
    prices = pd.read_csv(DATA_DIR / "latest_prices.csv", parse_dates=["Date"])
    forecast = pd.read_csv(DATA_DIR / "forecast_30d.csv", parse_dates=["Date"])
    summary = pd.read_csv(DATA_DIR / "forecast_summary.csv")
    return prices, forecast, summary

prices, forecast, summary = load_data()

st.title("🌾 Grain Futures Price Forecaster")
st.caption("Interactive decision-support dashboard for corn, wheat, and soybean futures.")

left, right = st.columns([2, 1])
with left:
    commodity_name = st.selectbox("Select commodity", list(COMMODITIES.keys()))
with right:
    st.metric("Alert threshold", f"±{ALERT_THRESHOLD_PCT:.1f}%")

ticker = COMMODITIES[commodity_name]
row = summary[summary["Ticker"] == ticker].iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Ticker", ticker)
m2.metric("Latest price", f"{row['LastPrice']:.2f}")
m3.metric("30D forecast", f"{row['Forecast30D']:.2f}", f"{row['ForecastChangePct']:.2f}%")
m4.metric("Signal", row["Signal"])

if row["Signal"] == "BUY/WATCH":
    st.success("Forecast indicates upward pressure. Review long exposure, procurement, and hedge strategy.")
elif row["Signal"] == "SELL/WATCH":
    st.error("Forecast indicates downward pressure. Review short exposure, inventory, and hedge strategy.")
else:
    st.info("Forecast movement is within the normal threshold. Current signal is HOLD.")

st.subheader("Historical price and 30-business-day forecast")
hist = prices[["Date", ticker]].rename(columns={ticker: "Price"}).dropna()
fc = forecast[forecast["Ticker"] == ticker][["Date", "ForecastPrice"]].rename(columns={"ForecastPrice": "Price"})
hist["Type"] = "Historical"
fc["Type"] = "Forecast"
chart_df = pd.concat([hist.tail(365), fc], ignore_index=True)
fig = px.line(chart_df, x="Date", y="Price", color="Type", title=f"{commodity_name} ({ticker})")
st.plotly_chart(fig, use_container_width=True)

st.subheader("All commodity signals")
st.dataframe(summary, use_container_width=True)

st.subheader("Cross-commodity latest prices")
latest = prices.sort_values("Date").tail(1).melt(id_vars="Date", var_name="Ticker", value_name="LatestPrice")
bar = px.bar(latest, x="Ticker", y="LatestPrice", title="Latest available futures prices")
st.plotly_chart(bar, use_container_width=True)

st.subheader("Forecast table")
st.dataframe(forecast[forecast["Ticker"] == ticker], use_container_width=True)

st.warning("This dashboard is for analytics and decision support only. It is not financial advice and does not execute trades.")
