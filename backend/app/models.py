from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey,
    JSON, Date, Boolean, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func          # pour timestamps auto
from database import Base

# 🧍 Table utilisateur
class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True)
    age             = Column(Integer, nullable=False)
    revenu          = Column(Float,   nullable=False)
    horizon         = Column(Integer, nullable=False)              # ➜ durée d’investissement (années)
    risk_aversion   = Column(String,  nullable=False)              # "faible", "moyenne", "élevée"
    objectif        = Column(String,  nullable=False)              # ex : "croissance agressive"
    esg_preference  = Column(Boolean, default=False)               # préférence ESG
    profil          = Column(String,  nullable=False)              # "conservateur", "modéré", "dynamique"
    risk_score      = Column(Float,   nullable=False)              # score numérique (utile pour audit)

    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    # Relation : un utilisateur → N portefeuilles
    portfolios = relationship("Portfolio", back_populates="user")


# 💼 Table des actifs financiers (ETF, actions, crypto…)
class Asset(Base):
    __tablename__ = "assets"

    id         = Column(Integer, primary_key=True)
    nom        = Column(String, nullable=False)
    ticker     = Column(String, nullable=False, unique=True)
    classe     = Column(String, nullable=False)               # ex : "Action", "Obligation", "Crypto"
    esg_score  = Column(Float)                                # (optionnel) score ESG de l’actif


# 📊 Table portefeuille utilisateur
class Portfolio(Base):
    __tablename__ = "portfolios"

    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    date        = Column(Date)                                # date de génération
    poids_json  = Column(JSON)                                # {"AAPL": 0.3, "BTC": 0.7}
    risque      = Column(Float)                               # volatilité annualisée
    rendement   = Column(Float)                               # rendement espéré

    user = relationship("User", back_populates="portfolios")
