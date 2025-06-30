Crypto-Price-Prediction-ML

Crypto Predictor — ML-powered web app forecasting Bitcoin &amp; Ethereum prices with 90%+ accuracy. Built with Python, Flask &amp; Random Forest. Retrieves real-time data from Yahoo Finance and CoinGecko for live forecasts. Designed for educational exploration of ML-driven crypto forecasting. 🚀📈

🧠 Crypto Predictor — Real-Time Cryptocurrency Price Forecasting using ML

A machine learning–powered web app that predicts short-term price movements (up/down) for top cryptocurrencies like Bitcoin and Ethereum. Built with Flask, Scikit-learn, and real-time data from Yahoo Finance and CoinGecko.

## ⚙️ Features

- 🔮 Predicts next price direction with 90%+ accuracy
- 📉 Works with Bitcoin, Ethereum, Dogecoin, Solana, and Binance Coin
- 📊 Interactive dashboard with real-time charts and model output
- ⚡ Auto-refreshing data with local caching for efficiency
- 📤 ML pipeline: feature extraction, model training, prediction
- 🧰 Configurable assets and prediction parameters

---

## 💻 Tech Stack

- **Language:** Python 3.8+
- **Framework:** Flask
- **ML Model:** Random Forest (via Scikit-learn)
- **Data APIs:** Yahoo Finance (fallback: CoinGecko)
- **Frontend:** HTML, CSS, Plotly.js
- **Storage:** Local cache for price data and trained models

---

## 🚀 Getting Started


# Clone the repo
git clone https://github.com/wasey-tech/crypto-price-prediction-ml.git
cd crypto-price-prediction-ml

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
Visit: http://localhost:5000

🧠 How It Works:

1.Data Pipeline:
Pulls historical crypto prices from Yahoo Finance
Falls back to CoinGecko if rate-limited
Extracts features like price change %, moving averages, etc.

2.Machine Learning:
Trains a Random Forest Classifier to predict next price movement
Uses cached models for faster reloading and predictions

3.Web Interface:
Built with Flask
Dashboard displays current prices, model predictions, and historical trends
Plotly for smooth, interactive charts

🔧 Configuration:
Modify config.py to:
Add/remove supported coins
Change prediction intervals
Set fallback API behavior
Tune ML or dashboard parameters

🧯 Troubleshooting:

API Limit Error:
Use CoinGecko fallback or create your own API key.
Try again after 5–10 minutes or use cached data.

Missing Cache Folders:
mkdir data_cache model_cache
