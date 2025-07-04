from typing import Tuple


def classify_profile(
    age: int,
    risk_aversion: str,
    horizon: int,
    revenu: float,
    objectif: str,
    esg_preference: bool,
) -> Tuple[float, str]:
    """
    Retourne (risk_score, profil).
    risk_score ∈ [0, 2] : plus il est élevé, plus l'utilisateur tolère le risque.
    profil : "conservateur", "modéré" ou "dynamique".
    """

    # --- Pondérations (somme = 1.0)
    W_AGE = 0.20
    W_RISK_AV = 0.35
    W_HORIZON = 0.20
    W_REVENU = 0.10
    W_OBJECTIF = 0.10
    W_ESG = -0.05  # ESG réduit légèrement la prise de risque

    # 1) Age
    if age < 30:
        score_age = 2
    elif age <= 50:
        score_age = 1
    else:
        score_age = 0

    # 2) Risk aversion (énum "faible", "moyenne", "élevée")
    mapping_risk = {"faible": 2, "moyenne": 1, "élevée": 0}
    score_risk_av = mapping_risk.get(risk_aversion.lower(), 1)

    # 3) Horizon (années)
    if horizon > 7:
        score_horizon = 2
    elif horizon > 3:
        score_horizon = 1
    else:
        score_horizon = 0

    # 4) Revenu annuel (€)
    if revenu > 80000:
        score_revenu = 2
    elif revenu > 40000:
        score_revenu = 1
    else:
        score_revenu = 0

    # 5) Objectif d’investissement
    mapping_obj = {
        "croissance agressive": 2,
        "croissance modérée": 1,
        "préservation du capital": 0,
    }
    score_obj = mapping_obj.get(objectif.lower(), 1)

    # 6) Préférence ESG (bonus prudence)
    score_esg = 0
    if esg_preference:
        score_esg = -0.5  # réduit le score global

    # --- Calcul du score pondéré (entre 0 et 2)
    weighted = (
        score_age * W_AGE
        + score_risk_av * W_RISK_AV
        + score_horizon * W_HORIZON
        + score_revenu * W_REVENU
        + score_obj * W_OBJECTIF
        + score_esg * W_ESG  # W_ESG est négatif pour diminuer le score
    )
    # Normaliser sur 0‑2 (optionnel mais pratique)
    risk_score = max(0.0, min(2.0, round(weighted, 2)))

    # --- Classification finale
    if risk_score <= 0.8:
        profil = "conservateur"
    elif risk_score <= 1.4:
        profil = "modéré"
    else:
        profil = "dynamique"

    return risk_score, profil