from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey,
    JSON, Date, Boolean, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    age = Column(Integer, nullable=False)
    revenu = Column(Float, nullable=False)
    horizon = Column(Integer, nullable=False)  # Durée d'investissement en années
    risk_aversion = Column(String, nullable=False)  # "faible", "moyenne", "élevée"
    objectif = Column(String, nullable=False)  # Ex: "croissance agressive"
    esg_preference = Column(Boolean, default=False)
    profil = Column(String, nullable=False)  # "conservateur", "modéré", "dynamique"
    risk_score = Column(Float, nullable=False)  # Score numérique

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relation : un utilisateur → plusieurs portefeuilles
    portfolios = relationship("Portfolio", back_populates="user")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    ticker = Column(String, nullable=False, unique=True)
    classe = Column(String, nullable=False)  # Ex: "Action", "Obligation", "Crypto"
    esg_score = Column(Float, nullable=True)  # Score ESG optionnel

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)  # Date de génération
    poids_json = Column(JSON, nullable=False)  # Exemple: {"AAPL": 0.3, "BTC": 0.7}
    risque = Column(Float, nullable=False)  # Volatilité annualisée
    rendement = Column(Float, nullable=False)  # Rendement espéré

    user = relationship("User", back_populates="portfolios")
