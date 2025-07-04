# backend/app/main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Tuple

# ⬇️ Importations internes
from database import Base, engine, SessionLocal
from models import User, Asset, Portfolio
from schemas.user import UserProfileIn, UserProfileOut
from services.profiling import classify_profile

# 🚀 Initialisation de l'app FastAPI
app = FastAPI(title="Robo‑Advisor API", version="0.1.0")

# ⚙️ Création automatique des tables
Base.metadata.create_all(bind=engine)

# 📦 Dépendance pour la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🧪 Endpoint racine pour tester l'API
@app.get("/")
def read_root():
    return {"message": "Hello, la base est prête 🐘"}

# 📥 Endpoint principal pour recevoir les données du questionnaire
@app.post("/submit_profile", response_model=UserProfileOut)
def submit_profile(payload: UserProfileIn, db: Session = Depends(get_db)):
    """
    Reçoit le profil utilisateur, calcule son score et classification,
    enregistre dans la base, et retourne le profil complet.
    """
    # Calcul du score + classification
    risk_score, profil = classify_profile(
        age=payload.age,
        risk_aversion=payload.risk_aversion.value,
        horizon=payload.horizon,
        revenu=payload.revenu,
        objectif=payload.objectif.value,
        esg_preference=payload.esg_preference
    )

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

    return user_db
