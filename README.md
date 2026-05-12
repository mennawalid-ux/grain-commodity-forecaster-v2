# Grain Commodity Forecaster

Interactive Streamlit website for grain futures analytics and daily decision support.

## Commodities

- Corn Futures: `ZC=F`
- Wheat Futures: `ZW=F`
- Soybean Futures: `ZS=F`

## Features

- Extracts daily futures prices from Yahoo Finance using `yfinance`
- Forecasts the next 30 business days
- Shows interactive historical and forecast charts
- Generates trading desk signals: `BUY/WATCH`, `SELL/WATCH`, or `HOLD`
- Sends Telegram alerts when forecast movement exceeds the threshold
- Automates daily updates with GitHub Actions
- Ready for Streamlit Cloud deployment

## Deploy on Streamlit Cloud

1. Upload all files to your GitHub repository.
2. Go to Streamlit Cloud.
3. Click **New app**.
4. Repository: your GitHub repo.
5. Branch: `main`.
6. Main file path: `app.py`.
7. Open **Advanced settings** and choose Python `3.11`.
8. Deploy.

## Local setup

```bash
pip install -r requirements.txt
python scripts/fetch_data.py
python scripts/train_forecast.py
streamlit run app.py
```

## Optional Telegram alerts

Add these GitHub repository secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Alerts are sent only when forecast movement is above the configured threshold.

## Important note

This tool is decision support only. It is not financial advice and should not place trades automatically.
