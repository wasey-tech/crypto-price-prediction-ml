import joblib
import numpy as np
import pandas as pd
import os
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from data_processor import get_all_crypto_data
from config import CRYPTOS

# Remove the existing CRYPTOS definition

# Update the predict_all method:
def predict_all(self):
    """Predict all cryptocurrencies"""
    results = {}
    for symbol in CRYPTOS.keys():  # Use the imported CRYPTOS
        results[symbol] = self.predict(symbol)
    return results

MODEL_CACHE_DIR = "model_cache"
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

class CryptoPredictor:
    def __init__(self):
        self.models = {}
        self.accuracy = {}
    
    def train_models(self):
        """Train models using cached data"""
        crypto_data = get_all_crypto_data()
        
        for symbol, crypto in crypto_data.items():
            data = crypto['data']
            
            # Skip if we don't have target data
            if 'Target' not in data.columns:
                continue
                
            model_file = os.path.join(MODEL_CACHE_DIR, f"{symbol}_model.joblib")
            
            # Load cached model if available
            if os.path.exists(model_file):
                try:
                    model, accuracy = joblib.load(model_file)
                    self.models[symbol] = model
                    self.accuracy[symbol] = accuracy
                    print(f"Loaded cached model for {symbol}")
                    continue
                except:
                    print(f"Failed to load cached model for {symbol}")
                    pass
                
            # Prepare features and target
            features = data.drop(['Target', 'Future_3D'], axis=1, errors='ignore')
            target = data['Target']
            
            # Skip if not enough data for split
            if len(features) < 20:
                continue
                
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=0.2, shuffle=False
            )
            
            # Use simpler model for reliability
            model = RandomForestClassifier(
                n_estimators=50,
                max_depth=5,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train, y_train)
            
            # Evaluate model
            accuracy = 0
            if len(y_test) > 0:
                predictions = model.predict(X_test)
                accuracy = accuracy_score(y_test, predictions) * 100
            
            # Store results
            self.models[symbol] = model
            self.accuracy[symbol] = accuracy
            
            # Cache model
            joblib.dump((model, accuracy), model_file)
            print(f"Trained and cached model for {symbol}")
    
    def predict(self, symbol):
        """Predict the next 3 days for a cryptocurrency"""
        if symbol not in self.models:
            return None
        
        crypto_data = get_all_crypto_data()
        if symbol not in crypto_data:
            return None
            
        data = crypto_data[symbol]['data']
        if data.empty:
            return None
        
        try:
            # Get the most recent data point
            latest = data.iloc[-1].drop(['Target', 'Future_3D'], errors='ignore')
            latest_df = pd.DataFrame([latest])
            
            # Make prediction
            model = self.models[symbol]
            prediction = model.predict(latest_df)[0]
            prediction_prob = model.predict_proba(latest_df)[0][1] * 100
            
            return {
                'prediction': prediction,
                'probability': prediction_prob,
                'accuracy': self.accuracy[symbol]
            }
        except Exception as e:
            print(f"Prediction error for {symbol}: {e}")
            return None
    
    def predict_all(self):
        """Predict all cryptocurrencies"""
        results = {}
        for symbol in CRYPTOS.keys():
            results[symbol] = self.predict(symbol)
        return results