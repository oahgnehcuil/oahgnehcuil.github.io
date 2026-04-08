import yfinance as yf
import pandas as pd

# 定義 DAT 公司清單
tickers = ["MSTR", "MARA", "COIN", "TSLA", "BTC-USD"]

def get_financial_summary():
    summary_data = []
    for t in tickers:
        stock = yf.Ticker(t)
        info = stock.info
        summary_data.append({
            "Symbol": t,
            "Price": info.get("currentPrice", info.get("regularMarketPrice")),
            "MarketCap": info.get("marketCap"),
            "52WeekChange": info.get("52WeekChange")
        })
    
    df = pd.DataFrame(summary_data)
    # 將結果轉存為 HTML 表格片段，供 index.html 使用
    df.to_html("data_table.html", index=False, classes="styled-table")
    print("Data updated!")

if __name__ == "__main__":
    get_financial_summary()