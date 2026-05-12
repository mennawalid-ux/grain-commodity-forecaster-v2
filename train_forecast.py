from pathlib import Path
import pandas as pd
import numpy as np
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from config import COMMODITIES, FORECAST_DAYS, ALERT_THRESHOLD_PCT

DATA_DIR = ROOT / "data"


def linear_forecast(series: pd.Series, days: int = FORECAST_DAYS) -> pd.Series:
    clean = series.dropna().astype(float)
    if len(clean) < 30:
        last = clean.iloc[-1] if len(clean) else np.nan
        return pd.Series([last] * days)

    recent = clean.tail(180)
    x = np.arange(len(recent))
    y = recent.values
    slope, intercept = np.polyfit(x, y, 1)
    future_x = np.arange(len(recent), len(recent) + days)
    forecast = intercept + slope * future_x
    forecast = np.maximum(forecast, 0)
    return pd.Series(forecast)


def signal_from_change(change_pct: float) -> str:
    if change_pct >= ALERT_THRESHOLD_PCT:
        return "BUY/WATCH"
    if change_pct <= -ALERT_THRESHOLD_PCT:
        return "SELL/WATCH"
    return "HOLD"


if __name__ == "__main__":
    prices_path = DATA_DIR / "latest_prices.csv"
    prices = pd.read_csv(prices_path, parse_dates=["Date"])
    last_date = prices["Date"].max()
    future_dates = pd.bdate_range(last_date + pd.Timedelta(days=1), periods=FORECAST_DAYS)

    forecast_rows = []
    summary_rows = []

    for name, ticker in COMMODITIES.items():
        fc = linear_forecast(prices[ticker], FORECAST_DAYS)
        last_price = float(prices[ticker].dropna().iloc[-1])
        forecast_end = float(fc.iloc[-1])
        change_pct = ((forecast_end - last_price) / last_price) * 100
        signal = signal_from_change(change_pct)

        for date, value in zip(future_dates, fc):
            forecast_rows.append({
                "Date": date.date(),
                "Commodity": name,
                "Ticker": ticker,
                "ForecastPrice": round(float(value), 4),
            })

        summary_rows.append({
            "Commodity": name,
            "Ticker": ticker,
            "LastPrice": round(last_price, 4),
            "Forecast30D": round(forecast_end, 4),
            "ForecastChangePct": round(change_pct, 2),
            "Signal": signal,
            "Alert": abs(change_pct) >= ALERT_THRESHOLD_PCT,
        })

    pd.DataFrame(forecast_rows).to_csv(DATA_DIR / "forecast_30d.csv", index=False)
    pd.DataFrame(summary_rows).to_csv(DATA_DIR / "forecast_summary.csv", index=False)
    print("Saved forecast_30d.csv and forecast_summary.csv")
