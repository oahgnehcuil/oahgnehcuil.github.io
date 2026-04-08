from flask import Flask, jsonify, render_template
from flask_cors import CORS
import yfinance as yf
import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Data storage file
DATA_FILE = 'mnav_data.json'

def load_historical_data():
    """Load historical data from file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"data": []}

def save_historical_data(data):
    """Save historical data to file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_mnav_data():
    """Calculate current MNAV data"""
    # 定義 DAT 公司：MicroStrategy (MSTR)
    # 假設持有量 (依據 2026 年初公開數據，請視作業需求調整)
    mstr_holdings = 252220
    
    try:
        # 抓取資料
        mstr = yf.Ticker("MSTR")
        btc = yf.Ticker("BTC-USD")
        
        mstr_price = mstr.history(period="1d")['Close'].iloc[-1]
        btc_price = btc.history(period="1d")['Close'].iloc[-1]
        
        # 抓取財報中的 Total Equity (簡化版計算)
        try:
            balance_sheet = mstr.balance_sheet
            if not balance_sheet.empty:
                # 嘗試不同的欄位名稱
                if 'Total Assets' in balance_sheet.index:
                    total_assets = balance_sheet.loc['Total Assets'].iloc[0]
                elif 'TotalAssets' in balance_sheet.index:
                    total_assets = balance_sheet.loc['TotalAssets'].iloc[0]
                else:
                    total_assets = balance_sheet.iloc[0].iloc[0]
                
                if 'Total Liabilities Net Minority Interest' in balance_sheet.index:
                    total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0]
                elif 'Total Liab' in balance_sheet.index:
                    total_liabilities = balance_sheet.loc['Total Liab'].iloc[0]
                else:
                    total_liabilities = balance_sheet.iloc[1].iloc[0] if len(balance_sheet) > 1 else 0
                
                equity = total_assets - total_liabilities
            else:
                # 如果無法獲取財報數據，使用市場估計
                equity = mstr.info.get('totalAssets', 0) - mstr.info.get('totalLiab', 0)
        except Exception as e:
            print(f"Balance sheet error: {e}")
            # 使用備用計算方法
            equity = mstr.info.get('totalAssets', 0) - mstr.info.get('totalLiab', 0)
            
        # 如果仍然為零，使用市場資本作為替代
        if equity <= 0:
            equity = mstr.info.get('marketCap', 0)
        
        # 計算 MNAV (假設原本帳面價值已扣除，此為溢價調整後估值)
        mnav = equity + (mstr_holdings * btc_price)
        market_cap = mstr.info.get('marketCap', mstr_price * mstr.info.get('sharesOutstanding', 1))
        premium = (market_cap / mnav - 1) * 100

        return {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mstr_price": round(mstr_price, 2),
            "btc_price": round(btc_price, 2),
            "mnav": round(mnav / 1e9, 2), # 以十億為單位
            "premium": round(premium, 2),
            "market_cap": round(market_cap / 1e9, 2)  # 以十億為單位
        }
    except Exception as e:
        print(f"Error calculating MNAV: {e}")
        return None

def update_data():
    """Update historical data with current values"""
    current_data = get_mnav_data()
    if current_data:
        historical_data = load_historical_data()
        
        # Check if today's data already exists
        today = current_data["date"]
        existing_data = [d for d in historical_data["data"] if d["date"] == today]
        
        if not existing_data:
            historical_data["data"].append(current_data)
            # Keep only last 30 days of data
            historical_data["data"] = historical_data["data"][-30:]
            save_historical_data(historical_data)
        
        return current_data
    return None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/current')
def get_current():
    """Get current MNAV data"""
    data = update_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Failed to fetch data"}), 500

@app.route('/api/historical')
def get_historical():
    """Get historical MNAV data"""
    historical_data = load_historical_data()
    return jsonify(historical_data)

@app.route('/api/update')
def update_endpoint():
    """Manual update endpoint"""
    data = update_data()
    if data:
        return jsonify({"status": "success", "data": data})
    return jsonify({"error": "Failed to update data"}), 500

if __name__ == '__main__':
    # Initialize data on first run
    update_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
