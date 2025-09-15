from typing import Dict
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    # Charger les prix historiques (tu peux adapter le chemin)
    prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)
    
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)
    
    if profil == "conservateur":
        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe()
    elif profil == "modéré":
        ef = EfficientFrontier(mu, S)
        weights = ef.efficient_risk(target_volatility=0.15)  # exemple cible
    else:  # dynamique
        ef = EfficientFrontier(mu, S)
        weights = ef.efficient_risk(target_volatility=0.25)  # plus risqué

    cleaned_weights = ef.clean_weights()
    return cleaned_weights
def get_assets_for_profile(profil: str) -> dict:
    """
    Retourne la répartition des classes d'actifs pour un profil donné.
    """
    profil = profil.lower()
    allocation = PROFILE_ALLOCATIONS.get(profil, {})
    return allocation


