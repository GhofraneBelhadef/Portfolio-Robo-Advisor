import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pypfopt import expected_returns, risk_models, EfficientFrontier



returns = pd.read_csv("returns.csv", index_col=0, parse_dates=True)


weights = {
    "AAPL": 0.15,
    "MSFT": 0.15,
    "TSLA": 0.10,
    "BND": 0.15,
    "AGG": 0.15,
    "TLT": 0.10,
    "BTC-USD": 0.10,
    "ETH-USD": 0.10
}


weights_array = np.array([weights[ticker] for ticker in returns.columns])


portfolio_returns = returns.dot(weights_array)


mean_return = portfolio_returns.mean() * 252  # annualisé
volatility = portfolio_returns.std() * np.sqrt(252)  # annualisée
sharpe_ratio = mean_return / volatility

print(f"Rendement annuel moyen : {mean_return:.2%}")
print(f"Volatilité annuelle : {volatility:.2%}")
print(f"Sharpe Ratio : {sharpe_ratio:.2f}")


cumulative_returns = (1 + portfolio_returns).cumprod()
cumulative_returns.plot(title="Évolution du portefeuille", figsize=(12,6))
plt.ylabel("Valeur cumulée")
plt.grid(True)
plt.show()
