from sqlalchemy import Column, Integer, String, Float, Boolean, Enum
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    revenu = Column(Float, nullable=False)
    horizon = Column(Integer, nullable=False)
    risk_aversion = Column(String, nullable=False)
    objectif = Column(String, nullable=False)
    esg_preference = Column(Boolean, default=False)
    profil = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False)
