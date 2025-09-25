from typing import Dict
import pandas as pd
import numpy as np
from pypfopt import expected_returns, risk_models, EfficientFrontier

ASSET_CLASSES = {
    "obligations": ["BND", "AGG", "TLT"],
    "actions": ["AAPL", "MSFT", "TSLA"],
    "crypto": ["BTC-USD", "ETH-USD"]
}

PROFILE_ALLOCATIONS = {
    "conservateur": {
        "obligations": 0.7,
        "actions": 0.25,
        "crypto": 0.05
    },
    "modéré": {
        "actions": 0.5,
        "obligations": 0.4,
        "crypto": 0.1
    },
    "dynamique": {
        "actions": 0.7,
        "crypto": 0.2,
        "obligations": 0.1
    }
}

def generate_initial_portfolio(profil: str) -> dict:
    prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)

    if profil == "conservateur":
        ef = EfficientFrontier(mu, S)
        ef.max_sharpe()
    elif profil == "modéré":
        ef = EfficientFrontier(mu, S)
        ef.efficient_risk(target_volatility=0.15)
    else:
        ef = EfficientFrontier(mu, S)
        ef.efficient_risk(target_volatility=0.25)

    return ef.clean_weights()

def get_assets_for_profile(profil: str) -> dict:
    profil = profil.lower()
    return PROFILE_ALLOCATIONS.get(profil, {})

def compute_historical_performance(prices: pd.DataFrame, weights: dict) -> dict:
    """
    Simulate historical portfolio performance.
    Returns: {'dates': list of dates, 'cumulative_returns': list of cumulative returns}
    """
    # Filter prices to only include assets with weights > 0
    valid_tickers = [t for t, w in weights.items() if w > 0 and t in prices.columns]
    if not valid_tickers:
        print("Warning: No valid tickers for backtest")  # Debug log
        return {'error': 'No valid tickers for backtest'}
    
    prices_subset = prices[valid_tickers].dropna()
    
    if prices_subset.empty:
        print("Warning: prices_subset is empty after dropna")  # Debug log
        return {'error': 'No valid price data after filtering'}
    
    # Compute daily returns
    returns = prices_subset.pct_change().dropna()
    
    if returns.empty:
        print(f"Warning: returns is empty (only {len(prices_subset)} rows in subset)")  # Debug log
        return {'error': 'Insufficient data for returns calculation'}
    
    # Portfolio daily returns (weighted)
    port_returns = returns.dot(np.array([weights[t] for t in valid_tickers]))
    
    # Cumulative returns (assuming starting value of 1)
    cumulative_returns = (1 + port_returns).cumprod()
    
    result = {
        'dates': cumulative_returns.index.strftime('%Y-%m-%d').tolist(),
        'cumulative_returns': cumulative_returns.tolist()
    }
    print(f"Success: Generated {len(result['dates'])} performance points")  # Debug log
    return result

def compute_efficient_frontier_points(prices: pd.DataFrame, num_points: int = 20) -> list:
    """
    Compute points along the efficient frontier for plotting.
    Returns: list of {'risk': float, 'return': float}
    """
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)
    
    # Compute bounds for volatility range
    min_vol = 0.05
    max_vol = 0.30
    try:
        ef_min = EfficientFrontier(mu, S)
        ef_min.min_volatility()
        _, min_risk, _ = ef_min.portfolio_performance()
        min_vol = float(min_risk)
        
        ef_max = EfficientFrontier(mu, S)
        ef_max.max_sharpe()  # Use max_sharpe instead of max_return
        _, max_risk, _ = ef_max.portfolio_performance()
        max_vol = float(max_risk)
        if max_vol < 0.30:
            max_vol = 0.30  # Extend if needed
        print(f"Frontier bounds: min_vol={min_vol:.4f}, max_vol={max_vol:.4f}")  # Debug log
    except Exception as e:
        print(f"Warning: Failed to compute bounds ({e}), using defaults")
    
    # Generate points by varying target volatility
    points = []
    volatilities = np.linspace(min_vol * 0.9, max_vol * 1.1, num_points)  # Slight buffer
    success_count = 0
    for target_vol in volatilities:
        ef = EfficientFrontier(mu, S)  # NEW: Create fresh ef each iteration
        try:
            ef.efficient_risk(target_vol)
            ret, risk, _ = ef.portfolio_performance()
            points.append({'risk': float(risk), 'return': float(ret)})
            success_count += 1
        except Exception as e:
            print(f"Skipped vol {target_vol:.4f}: {e}")  # Debug log (comment out in prod)
            continue
    
    print(f"Generated {success_count} frontier points")  # Debug log
    return points