import streamlit as st
import requests

st.title("Questionnaire Robo-Advisor simple")

age = st.number_input("Âge", min_value=18, max_value=100, value=30)
revenu = st.number_input("Revenu annuel (€)", min_value=0.0, value=30000.0)
horizon = st.number_input("Horizon d'investissement (années)", min_value=1, max_value=40, value=5)
risk_aversion = st.selectbox("Aversion au risque", ["faible", "moyenne", "élevée"])
objectif = st.selectbox("Objectif d'investissement", [
    "préservation du capital", "croissance modérée", "croissance agressive"])
esg_preference = st.checkbox("Préférence ESG")

if st.button("Envoyer"):
    data = {
        "age": age,
        "revenu": revenu,
        "horizon": horizon,
        "risk_aversion": risk_aversion,
        "objectif": objectif,
        "esg_preference": esg_preference,
    }
    try:
        response = requests.post("http://127.0.0.1:8000/submit_profile", json=data)
        if response.status_code == 200:
            st.success("Profil reçu !")
            st.json(response.json())
        else:
            st.error(f"Erreur {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
