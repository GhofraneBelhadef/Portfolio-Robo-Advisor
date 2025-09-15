from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Tuple
from fastapi.middleware.cors import CORSMiddleware
from services.portfolio_engine import generate_initial_portfolio
from services.portfolio_engine import generate_initial_portfolio, get_assets_for_profile

# ⬇️ Importations internes
from database import Base, engine, SessionLocal
from models import User, Asset, Portfolio
from schemas.user import UserProfileIn, UserProfileOut
from services.profiling import classify_profile
from services.rag_engine import get_recommendation_for_profile

# 🚀 Initialisation de l'app FastAPI
app = FastAPI(title="Robo‑Advisor API", version="0.1.0")

origins = [
    "http://localhost:5173",  # Your React app origin
    "http://localhost:3000",  # If you also use this in dev
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    # Add more if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Création automatique des tables
Base.metadata.create_all(bind=engine)

#  Dépendance pour la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  Endpoint racine pour tester l'API
@app.get("/")
def read_root():
    return {"message": "Hello, la base est prête 🐐"}

#  Endpoint principal pour recevoir les données du questionnaire
@app.post("/submit_profile", response_model=UserProfileOut)
def submit_profile(payload: UserProfileIn, db: Session = Depends(get_db)):
    """
    Reçoit le profil utilisateur, calcule son score et classification,
    enregistre dans la base, et retourne le profil complet avec une recommandation RAG.
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
    portfolio_alloc = generate_initial_portfolio(profil)
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
    # RAG: Génération de la recommandation à partir de documents PDF indexés
    rag_response = get_recommendation_for_profile(profil)
    print(">>> classes_actifs =", classes_actifs)
    print(">>> portfolio_alloc =", portfolio_alloc)
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
        "portfolio_alloc": portfolio_alloc
    }