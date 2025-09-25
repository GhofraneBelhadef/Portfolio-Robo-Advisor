from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Tuple
from fastapi.middleware.cors import CORSMiddleware
from services.portfolio_engine import generate_initial_portfolio, get_assets_for_profile, compute_efficient_frontier_points, compute_historical_performance
import pandas as pd
from pypfopt import expected_returns, risk_models, EfficientFrontier
import numpy as np
import matplotlib.pyplot as plt

# ⬇️ Importations internes
from database import Base, engine, SessionLocal
from models import User, Asset, Portfolio
from schemas.user import UserProfileIn, UserProfileOut
from services.profiling import classify_profile
from services.rag_engine import get_recommendation_for_profile

# 🚀 Initialisation de l'app FastAPI
app = FastAPI(title="Robo-Advisor API", version="0.1.0")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Création automatique des tables
Base.metadata.create_all(bind=engine)

# Dépendance pour la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello, la base est prête 🐐"}

@app.post("/submit_profile")
def submit_profile(payload: UserProfileIn, db: Session = Depends(get_db)):
    # Calcul du score + classification
    risk_score, profil = classify_profile(
        age=payload.age,
        risk_aversion=payload.risk_aversion.value,
        horizon=payload.horizon,
        revenu=payload.revenu,
        objectif=payload.objectif.value,
        esg_preference=payload.esg_preference
    )

    portfolio_alloc = generate_initial_portfolio(profil)
    
    # Charger les prix
    prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)
    prices = prices.dropna(axis=1, how="all")
    prices = prices.loc[:, (prices != 0).any()]

    if prices.empty:
        raise HTTPException(status_code=500, detail="Aucun ticker valide trouvé dans les données de prix")

    # Recalculer les rendements et covariance
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)
    ef = EfficientFrontier(mu, S)

    valid_weights = {t: w for t, w in portfolio_alloc.items() if t in prices.columns}
    if not valid_weights:
        raise HTTPException(status_code=500, detail="No overlap between portfolio_alloc and price data")

    ef_weights = [valid_weights.get(t, 0) for t in ef.tickers]
    ef.weights = np.array(ef_weights)
    user_ret, user_risk, _ = ef.portfolio_performance()

    # Compute visualization data (with fallback)
    sim_performance = {'error': 'Computation failed'}
    frontier_points = []
    try:
        sim_performance = compute_historical_performance(prices, portfolio_alloc)
        frontier_points = compute_efficient_frontier_points(prices)
    except Exception as e:
        print(f"Visualization computation error: {e}")  # Debug log
    
    # User's point on frontier
    user_point = {'risk': float(user_risk), 'return': float(user_ret)}

    # Création de l'utilisateur
    user_db = User(
        age=payload.age,
        revenu=payload.revenu,
        horizon=payload.horizon,
        risk_aversion=payload.risk_aversion.value,
        objectif=payload.objectif.value,
        esg_preference=payload.esg_preference,
        profil=profil,
        risk_score=risk_score,
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    classes_actifs = get_assets_for_profile(profil)
    rag_response = get_recommendation_for_profile(profil)

    return {
        "id": user_db.id,
        "age": user_db.age,
        "revenu": user_db.revenu,
        "horizon": user_db.horizon,
        "risk_aversion": user_db.risk_aversion,
        "objectif": user_db.objectif,
        "profil": user_db.profil,
        "risk_score": user_db.risk_score,
        "classes_actifs": classes_actifs,
        "recommendation": rag_response,
        "portfolio_alloc": portfolio_alloc, 
        "user_portfolio": {
            "risk": float(user_risk),
            "ret": float(user_ret)
        },
        "sim_performance": sim_performance,
        "frontier_points": frontier_points,
        "user_point": user_point
    }