import yfinance as yf

def calculate_mnav(stock_ticker, crypto_ticker, holdings_qty):
    # 1. 抓取公司財報與即時股價
    stock = yf.Ticker(stock_ticker)
    crypto = yf.Ticker(crypto_ticker)
    
    # 取得最新帳面淨值 (Total Stockholder Equity)
    balance_sheet = stock.balance_sheet
    if balance_sheet.empty:
        return "無法取得財報資料"
    
    book_value = balance_sheet.iloc[0]['Total Assets'] - balance_sheet.iloc[0]['Total Liabilities Net Minority Interest']
    
    # 2. 取得即時加密貨幣價格
    crypto_price = crypto.history(period="1d")['Close'].iloc[-1]
    
    # 3. 假設公司在財報中的加密貨幣帳面價值 (這部分通常以成本計，需查閱財報備註)
    # 這裡簡化計算：淨值調整 = (現值 - 成本)
    # 註：MSTR 現在採用公允價值會計準則，帳面價值可能已接近市價
    market_value_of_holdings = holdings_qty * crypto_price
    
    # 這裡的 Modified NAV 計算邏輯可以根據你的作業定義調整
    # 範例：市值 (Market Cap) / MNAV 常用來判斷溢價
    mnav = book_value + market_value_of_holdings 
    
    return {
        "Ticker": stock_ticker,
        "Book Value": book_value,
        "Crypto Market Value": market_value_of_holdings,
        "MNAV": mnav
    }

with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"<html><body><h1>MNAV: {mnav_result}</h1></body></html>")