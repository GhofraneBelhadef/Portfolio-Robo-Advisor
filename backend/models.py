from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from database import Base

# 🧍 Table utilisateur
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    revenu = Column(Float)
    objectif = Column(String)
    risque = Column(String)
    profil = Column(String)

    # Un utilisateur peut avoir plusieurs portefeuilles
    portfolios = relationship("Portfolio", back_populates="user")


# 💼 Table des actifs financiers (ETF, actions, crypto…)
class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    nom = Column(String)
    ticker = Column(String)
    classe = Column(String)


# 📊 Table portefeuille utilisateur
class Portfolio(Base):
    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    poids_json = Column(JSON)  # ex : {"AAPL": 0.3, "BTC": 0.7}
    risque = Column(Float)
    rendement = Column(Float)

    user = relationship("User", back_populates="portfolios")
