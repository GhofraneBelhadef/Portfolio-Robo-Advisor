from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, conint, confloat, validator, EmailStr
from typing import Dict



# ▸ Énumérations pour garantir des valeurs contrôlées
class RiskAversion(str, Enum):
    faible = "faible"
    moyenne = "moyenne"
    élevée = "élevée"


class InvestmentObjective(str, Enum):
    preservation = "préservation du capital"
    croissance_moderee = "croissance modérée"
    croissance_agressive = "croissance agressive"


# ▸ Modèle reçu depuis le frontend
class UserProfileIn(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Adresse email (optionnel)")
    age: conint(ge=18, le=100) = Field(..., description="Âge en années")
    revenu: confloat(gt=0) = Field(..., description="Revenu annuel en euros")
    horizon: conint(gt=0, le=40) = Field(..., description="Durée d’investissement (années)")
    risk_aversion: RiskAversion
    objectif: InvestmentObjective
    esg_preference: bool = Field(False, description="True si l'utilisateur veut privilégier ESG")

    # Validation additionnelle : un horizon très long suppose un âge cohérent
    @validator("horizon")
    def horizon_vs_age(cls, v, values):
        age = values.get("age")
        if age and age + v > 100:
            raise ValueError("Horizon trop long pour l'âge fourni")
        return v


# ▸ Modèle que le backend renvoie au frontend après classification
class UserProfileOut(UserProfileIn):
    profil: str            # "conservateur", "modéré", "dynamique"
    risk_score: float      # score numérique interne
    id: int                # identifiant en base
    # recommendation: str

    classes_actifs: Optional[Dict[str, float]] = None
    portfolio_alloc: Optional[Dict[str, float]] = None
    class Config:
        orm_mode = True    # permet de retourner directement un objet SQLAlchemy
