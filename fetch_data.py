from pathlib import Path
import pandas as pd
import yfinance as yf
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from config import COMMODITIES, DEFAULT_PERIOD, DEFAULT_INTERVAL

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


def fetch_prices() -> pd.DataFrame:
    tickers = list(COMMODITIES.values())
    raw = yf.download(
        tickers=tickers,
        period=DEFAULT_PERIOD,
        interval=DEFAULT_INTERVAL,
        auto_adjust=True,
        progress=False,
        group_by="column",
    )

    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"].copy()
    else:
        close = raw[["Close"]].copy()
        close.columns = tickers

    close = close.rename_axis("Date").reset_index()
    close["Date"] = pd.to_datetime(close["Date"]).dt.date
    close = close.dropna(how="all", subset=tickers)
    return close


if __name__ == "__main__":
    prices = fetch_prices()
    output = DATA_DIR / "latest_prices.csv"
    prices.to_csv(output, index=False)
    print(f"Saved {len(prices)} rows to {output}")
