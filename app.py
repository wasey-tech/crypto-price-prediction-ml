from flask import Flask, render_template
import predictor
import plotly
import plotly.graph_objs as go
import json
from datetime import datetime
from config import CRYPTOS

# Update the index route:

def index():
    try:
        # Train models only if needed
        if not crypto_predictor.models:
            crypto_predictor.train_models()
        
        # Get predictions
        predictions = crypto_predictor.predict_all()
        
        # Get crypto data for charts
        crypto_data = predictor.get_all_crypto_data()
        
        # Prepare data for the template
        crypto_info = []
        for symbol in CRYPTOS.keys():  # Use the imported CRYPTOS
            pred = predictions.get(symbol)
            if not pred or symbol not in crypto_data:
                continue
                
            name = CRYPTOS[symbol]  # Get name from config
            data = crypto_data[symbol]['data']
            
            # Skip if not enough data for chart
            if data.empty or len(data) < 10:
                continue
                
            # Create simplified chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=data['Close'],
                mode='lines',
                name='Price',
                line=dict(color='#1f77b4')
            ))
            
            fig.update_layout(
                title=f'{name} Price History',
                xaxis_title='Date',
                yaxis_title='Price (USD)',
                template='plotly_dark',
                showlegend=False,
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            crypto_info.append({
                'symbol': symbol,
                'name': name,
                'current_price': data['Close'].iloc[-1],
                'prediction': pred['prediction'],
                'probability': pred['probability'],
                'accuracy': pred['accuracy'],
                'chart': chart_json
            })
        
        # If we have no predictions, show error
        if not crypto_info:
            return render_template(
                'error.html',
                error_message="No predictions available. This usually means we couldn't fetch enough data from providers. Please try again later."
            )
        
        return render_template(
            'index.html',
            crypto_info=crypto_info,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template(
            'error.html',
            error_message=f"Failed to load predictions: {str(e)}"
        )

app = Flask(__name__)

# Initialize predictor
crypto_predictor = predictor.CryptoPredictor()

@app.route('/')
def index():
    try:
        # Train models only if needed
        if not crypto_predictor.models:
            crypto_predictor.train_models()
        
        # Get predictions
        predictions = crypto_predictor.predict_all()
        
        # Get crypto data for charts
        crypto_data = predictor.get_all_crypto_data()
        
        # Prepare data for the template
        crypto_info = []
        for symbol, pred in predictions.items():
            if not pred or symbol not in crypto_data:
                continue
                
            name = crypto_data[symbol]['name']
            data = crypto_data[symbol]['data']
            
            # Skip if not enough data for chart
            if data.empty or len(data) < 10:
                continue
                
            # Create simplified chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=data['Close'],
                mode='lines',
                name='Price',
                line=dict(color='#1f77b4')
            ))
            
            fig.update_layout(
                title=f'{name} Price History',
                xaxis_title='Date',
                yaxis_title='Price (USD)',
                template='plotly_dark',
                showlegend=False,
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            crypto_info.append({
                'symbol': symbol,
                'name': name,
                'current_price': data['Close'].iloc[-1],
                'prediction': pred['prediction'],
                'probability': pred['probability'],
                'accuracy': pred['accuracy'],
                'chart': chart_json
            })
        
        # If we have no predictions, show error
        if not crypto_info:
            return render_template(
                'error.html',
                error_message="No predictions available. This usually means we couldn't fetch enough data from providers. Please try again later."
            )
        
        return render_template(
            'index.html',
            crypto_info=crypto_info,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template(
            'error.html',
            error_message="Failed to load predictions. Please try again later."
        )

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)