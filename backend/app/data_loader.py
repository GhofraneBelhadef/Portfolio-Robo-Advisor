import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

tickers = ["AAPL", "MSFT", "TSLA", "BND", "AGG", "TLT", "BTC-USD", "ETH-USD"]
start_date = "2020-01-01"
end_date = "2024-08-01"


data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker', auto_adjust=True)


adj_close = pd.DataFrame({ticker: data[ticker]['Close'] for ticker in tickers})

adj_close.dropna(inplace=True)


print(adj_close.head())

adj_close.plot(figsize=(12, 6), title="Prix ajustés des actifs")
plt.show()


returns = adj_close.pct_change().dropna()


adj_close.to_csv("prices.csv")
returns.to_csv("returns.csv")
