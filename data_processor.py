import yfinance as yf
import pandas as pd
import numpy as np
import os
import time
import json
import requests
from datetime import datetime, timedelta
from config import CRYPTOS, COINGECKO_MAP

# Cryptocurrencies to track
CRYPTOS = {
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    'BNB-USD': 'Binance Coin',
    'DOGE-USD': 'Dogecoin',
    'SOL-USD': 'Solana'
}

# Create cache directory
CACHE_DIR = "data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_crypto_data(symbol, days=90):
    """Fetch cryptocurrency data from multiple sources with fallback"""
    cache_file = os.path.join(CACHE_DIR, f"{symbol}.json")
    
    # Use cache if less than 2 hours old
    if os.path.exists(cache_file):
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if file_age < timedelta(hours=2):
            try:
                return pd.read_json(cache_file)
            except:
                pass
    
    # Try Yahoo Finance
    data = fetch_yahoo_data(symbol, days)
    if not data.empty:
        data.to_json(cache_file)
        return data
    
    # Try CoinGecko as fallback
    data = fetch_coingecko_data(symbol, days)
    if not data.empty:
        data.to_json(cache_file)
        return data
    
    # Return cached data even if outdated
    if os.path.exists(cache_file):
        try:
            return pd.read_json(cache_file)
        except:
            pass
    
    return pd.DataFrame()

def fetch_yahoo_data(symbol, days):
    """Fetch data from Yahoo Finance with retries"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            time.sleep(5 * attempt + 1)  # Increasing delay
            data = yf.download(symbol, period=f'{days}d', progress=False)
            if not data.empty:
                return data
        except Exception as e:
            print(f"Yahoo attempt {attempt+1} failed for {symbol}: {e}")
            time.sleep(5)
    return pd.DataFrame()

def fetch_coingecko_data(symbol, days):
    """Fetch data from CoinGecko API"""
    coin_id_map = {
        'BTC-USD': 'bitcoin',
        'ETH-USD': 'ethereum',
        'BNB-USD': 'binancecoin',
        'DOGE-USD': 'dogecoin',
        'SOL-USD': 'solana'
    }
    
    coin_id = coin_id_map.get(symbol)
    if not coin_id:
        return pd.DataFrame()
    
    try:
        # Get historical data from CoinGecko
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process data
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('date', inplace=True)
        
        # Create OHLC structure
        ohlc = df['price'].resample('D').ohlc()
        ohlc.columns = ['Open', 'High', 'Low', 'Close']
        
        # Add volume (not available in free API)
        ohlc['Volume'] = 0
        
        return ohlc.dropna()
    
    except Exception as e:
        print(f"CoinGecko failed for {symbol}: {e}")
        return pd.DataFrame()

def process_data(data):
    """Process cryptocurrency data"""
    if data.empty or len(data) < 10:
        return data
    
    # Basic processing
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    data = data.dropna()
    
    # Add technical indicators
    if len(data) > 7:
        data['MA7'] = data['Close'].rolling(window=7).mean()
    if len(data) > 30:
        data['MA30'] = data['Close'].rolling(window=30).mean()
    
    # Add momentum
    if len(data) > 4:
        data['Momentum'] = data['Close'] - data['Close'].shift(4)
    
    # Add target
    if len(data) > 3:
        data['Future_3D'] = data['Close'].shift(-3)
        data['Target'] = (data['Future_3D'] > data['Close']).astype(int)
    
    return data.dropna()

def get_all_crypto_data():
    """Fetch and process data for all cryptocurrencies"""
    crypto_data = {}
    
    for symbol, name in CRYPTOS.items():
        print(f"Fetching data for {name}...")
        raw_data = fetch_crypto_data(symbol)
        processed_data = process_data(raw_data)
        
        # If we don't have enough data, skip this crypto
        if processed_data.empty or len(processed_data) < 20:
            print(f"⚠️ Insufficient data for {name}. Skipping.")
            continue
            
        crypto_data[symbol] = {
            'name': name,
            'data': processed_data
        }
        
        # Add delay between requests
        time.sleep(5)
    
    return crypto_data