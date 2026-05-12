from pathlib import Path
import os
import requests
import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
load_dotenv(ROOT / ".env")


def send_telegram(message: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram secrets are not configured. Skipping alert.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=20)
    response.raise_for_status()
    print("Telegram alert sent.")


if __name__ == "__main__":
    summary_path = DATA_DIR / "forecast_summary.csv"
    if not summary_path.exists():
        print("No forecast summary found. Run train_forecast.py first.")
        raise SystemExit(0)

    summary = pd.read_csv(summary_path)
    alerts = summary[summary["Alert"] == True]
    if alerts.empty:
        print("No alert triggered.")
        raise SystemExit(0)

    lines = ["Grain Futures Forecast Alert"]
    for _, row in alerts.iterrows():
        lines.append(
            f"{row['Commodity']} ({row['Ticker']}): {row['Signal']} | "
            f"30D forecast change {row['ForecastChangePct']}% | "
            f"Last {row['LastPrice']} -> Forecast {row['Forecast30D']}"
        )
    send_telegram("\n".join(lines))
