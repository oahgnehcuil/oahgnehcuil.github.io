import yfinance as yf

# 1. 建立 Ticker 對象 (比特幣用 BTC-USD, 美股直接用代碼)
btc = yf.Ticker("BTC-USD")
mstr = yf.Ticker("MSTR")

# 2. 獲取當前價格 (Fast Info)
current_btc_price = btc.fast_info['last_price']
current_mstr_price = mstr.fast_info['last_price']

# 3. 獲取公司財務資訊 (市值、債務等)
# 注意：info 會發起多次請求，速度較慢，建議只抓一次並存在變數裡
mstr_info = mstr.info
market_cap = mstr_info.get('marketCap')
total_debt = mstr_info.get('totalDebt')

print(f"BTC 價格: {current_btc_price}")
print(f"MSTR 市值: {market_cap}")