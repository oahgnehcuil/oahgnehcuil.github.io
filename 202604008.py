import yfinance as yf
import datetime

def get_mnav():
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
        equity = mstr.balance_sheet.iloc[0]['Total Assets'] - mstr.balance_sheet.iloc[0]['Total Liabilities Net Minority Interest']
        
        # 計算 MNAV (假設原本帳面價值已扣除，此為溢價調整後估值)
        mnav = equity + (mstr_holdings * btc_price)
        market_cap = mstr.info.get('marketCap', mstr_price * mstr.info.get('sharesOutstanding', 1))
        premium = (market_cap / mnav - 1) * 100

        return {
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mstr_price": round(mstr_price, 2),
            "btc_price": round(btc_price, 2),
            "mnav": round(mnav / 1e9, 2), # 以十億為單位
            "premium": round(premium, 2)
        }
    except Exception as e:
        return f"Error: {e}"

data = get_mnav()

# 生成 HTML 檔案
html_template = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>DAT.co 監控平台</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; background: #f4f7f6; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }}
        .highlight {{ color: #0366d6; font-size: 24px; font-weight: bold; }}
        .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>MSTR 投資決策指標</h2>
        <p>比特幣現價: <span class="highlight">${data['btc_price']}</span></p>
        <p>估計 MNAV: <span class="highlight">${data['mnav']} B</span></p>
        <p>市場溢價率: <span class="highlight">{data['premium']}%</span></p>
        <hr>
        <p>這項指標可以協助判斷目前 MSTR 股價相對於其數位資產儲備是否過高。</p>
    </div>
    <div class="footer">最後更新時間：{data['time']} (UTC)</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)