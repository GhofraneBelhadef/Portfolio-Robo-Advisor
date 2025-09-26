from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Tuple
from fastapi.middleware.cors import CORSMiddleware
from services.portfolio_engine import generate_initial_portfolio, get_assets_for_profile, compute_efficient_frontier_points, compute_historical_performance
import pandas as pd
from pypfopt import expected_returns, risk_models, EfficientFrontier
import numpy as np
import matplotlib.pyplot as plt
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os

# ⬇️ Importations internes
from database import Base, engine, SessionLocal
from models import User
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
    
    # Filtrer les allocations à 0%
    portfolio_alloc = {asset: weight for asset, weight in portfolio_alloc.items() if weight > 0}

    # Charger les prix
    prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)
    prices = prices.dropna(axis=1, how="all")
    prices = prices.loc[:, (prices != 0).any()]

    if prices.empty:
        raise HTTPException(status_code=500, detail="Aucun ticker valide trouvé dans les données de prix")

    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)
    ef = EfficientFrontier(mu, S)

    valid_weights = {t: w for t, w in portfolio_alloc.items() if t in prices.columns}
    if not valid_weights:
        raise HTTPException(status_code=500, detail="No overlap between portfolio_alloc and price data")

    ef_weights = [valid_weights.get(t, 0) for t in ef.tickers]
    ef.weights = np.array(ef_weights)
    user_ret, user_risk, _ = ef.portfolio_performance()

    sim_performance = {'error': 'Computation failed'}
    frontier_points = []
    try:
        sim_performance = compute_historical_performance(prices, portfolio_alloc)
        frontier_points = compute_efficient_frontier_points(prices)
    except Exception as e:
        print(f"Visualization computation error: {e}")

    user_point = {'risk': float(user_risk), 'return': float(user_ret)}

    classes_actifs = get_assets_for_profile(profil)
    rag_response = get_recommendation_for_profile(profil)

    # Return without adding to DB
    return {
        "age": payload.age,
        "revenu": payload.revenu,
        "horizon": payload.horizon,
        "risk_aversion": payload.risk_aversion.value,
        "objectif": payload.objectif.value,
        "profil": profil,
        "risk_score": risk_score,
        "classes_actifs": classes_actifs,
        "recommendation": rag_response,
        "portfolio_alloc": portfolio_alloc,  # allocations à 0% exclues
        "user_portfolio": {
            "risk": float(user_risk),
            "ret": float(user_ret)
        },
        "sim_performance": sim_performance,
        "frontier_points": frontier_points,
        "user_point": user_point
    }
def generate_pdf_report(user_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Titre
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Rapport d'Investissement - Robo-Advisor")

    # Informations utilisateur
    c.setFont("Helvetica", 12)
    y_position = height - 80
    c.drawString(50, y_position, f"Profil: {user_data['profil']}")
    y_position -= 20
    c.drawString(50, y_position, f"Score de risque: {user_data['risk_score']}")
    y_position -= 20
    c.drawString(50, y_position, f"Âge: {user_data['age']}")
    y_position -= 20
    c.drawString(50, y_position, f"Revenu: {user_data['revenu']} €")
    y_position -= 20
    c.drawString(50, y_position, f"Horizon: {user_data['horizon']} ans")
    y_position -= 20
    c.drawString(50, y_position, f"Aversion au risque: {user_data['risk_aversion']}")
    y_position -= 20
    c.drawString(50, y_position, f"Objectif: {user_data['objectif']}")
    y_position -= 20
    c.drawString(50, y_position, f"Préférence ESG: {'Oui' if user_data['esg_preference'] else 'Non'}")

    # Allocation du portefeuille
    y_position -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Allocation du portefeuille")
    y_position -= 20
    c.setFont("Helvetica", 12)
    for asset, weight in user_data['portfolio_alloc'].items():
        if weight > 0:
            c.drawString(50, y_position, f"{asset}: {(weight * 100):.2f}%")
            y_position -= 20

    # Générer et ajouter le graphique en camembert
    y_position -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Graphique d'allocation")
    y_position -= 220

    # Créer le graphique en camembert avec matplotlib
    labels = [asset for asset, weight in user_data['portfolio_alloc'].items() if weight > 0]
    sizes = [weight * 100 for weight in user_data['portfolio_alloc'].values() if weight > 0]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.title("Allocation du portefeuille")
    pie_chart_path = "pie_chart.png"
    plt.savefig(pie_chart_path)
    plt.close()

    # Ajouter le graphique au PDF
    c.drawImage(ImageReader(pie_chart_path), 50, y_position, width=3*inch, height=3*inch)
    os.remove(pie_chart_path)  # Supprimer le fichier temporaire

    # Ajouter la performance simulée (si disponible)
    if user_data['sim_performance'] and not user_data['sim_performance'].get('error'):
        y_position -= 250
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Performance simulée historique")
        y_position -= 220

        # Créer le graphique de performance
        fig, ax = plt.subplots()
        ax.plot(user_data['sim_performance']['dates'], user_data['sim_performance']['cumulative_returns'])
        ax.set_title("Performance simulée (Rendement Cumulé)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Rendement")
        line_chart_path = "line_chart.png"
        plt.savefig(line_chart_path)
        plt.close()

        # Ajouter au PDF
        c.drawImage(ImageReader(line_chart_path), 50, y_position, width=3*inch, height=3*inch)
        os.remove(line_chart_path)

    # Ajouter la frontière efficiente (si disponible)
    if user_data['frontier_points'] and len(user_data['frontier_points']) > 0:
        y_position -= 250
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Frontière efficiente")
        y_position -= 220

        # Créer le graphique de la frontière
        fig, ax = plt.subplots()
        risks = [point['risk'] for point in user_data['frontier_points']]
        returns = [point['return'] for point in user_data['frontier_points']]
        ax.plot(risks, returns, label="Frontière efficiente")
        ax.scatter([user_data['user_point']['risk']], [user_data['user_point']['return']], color='orange', label="Votre portefeuille")
        ax.set_title("Frontière efficiente : Risque vs Rendement")
        ax.set_xlabel("Risque (%)")
        ax.set_ylabel("Rendement (%)")
        ax.legend()
        frontier_chart_path = "frontier_chart.png"
        plt.savefig(frontier_chart_path)
        plt.close()

        # Ajouter au PDF
        c.drawImage(ImageReader(frontier_chart_path), 50, y_position, width=3*inch, height=3*inch)
        os.remove(frontier_chart_path)

    # Recommandation
    y_position -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Recommandation")
    y_position -= 20
    c.setFont("Helvetica", 12)
    text = c.beginText(50, y_position)
    for line in user_data['recommendation'].split('\n'):
        text.textLine(line)
    c.drawText(text)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
@app.post("/generate_pdf")
async def generate_pdf(payload: UserProfileIn, db: Session = Depends(get_db)):
    # Réutiliser la logique de /submit_profile pour obtenir les données
    risk_score, profil = classify_profile(
        age=payload.age,
        risk_aversion=payload.risk_aversion.value,
        horizon=payload.horizon,
        revenu=payload.revenu,
        objectif=payload.objectif.value,
        esg_preference=payload.esg_preference
    )

    portfolio_alloc = generate_initial_portfolio(profil)
    prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True)
    prices = prices.dropna(axis=1, how="all")
    prices = prices.loc[:, (prices != 0).any()]

    if prices.empty:
        raise HTTPException(status_code=500, detail="Aucun ticker valide trouvé dans les données de prix")

    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)
    ef = EfficientFrontier(mu, S)

    valid_weights = {t: w for t, w in portfolio_alloc.items() if t in prices.columns}
    if not valid_weights:
        raise HTTPException(status_code=500, detail="No overlap between portfolio_alloc and price data")

    ef_weights = [valid_weights.get(t, 0) for t in ef.tickers]
    ef.weights = np.array(ef_weights)
    user_ret, user_risk, _ = ef.portfolio_performance()

    sim_performance = {'error': 'Computation failed'}
    frontier_points = []
    try:
        sim_performance = compute_historical_performance(prices, portfolio_alloc)
        frontier_points = compute_efficient_frontier_points(prices)
    except Exception as e:
        print(f"Visualization computation error: {e}")

    user_point = {'risk': float(user_risk), 'return': float(user_ret)}

    user_db = User(
        email=payload.email,
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

    # Données pour le PDF
    user_data = {
        "id": user_db.id,
        "age": user_db.age,
        "revenu": user_db.revenu,
        "horizon": user_db.horizon,
        "risk_aversion": user_db.risk_aversion,
        "objectif": user_db.objectif,
        "esg_preference": user_db.esg_preference,
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

    # Générer le PDF
    pdf_buffer = generate_pdf_report(user_data)

    # Retourner le PDF comme réponse
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=rapport_investissement.pdf"}
    )