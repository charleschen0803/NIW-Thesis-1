import yfinance as yf
data = yf.download("ADBE", start="2013-01-01", end="2023-12-31")
print(data.head())
