from database import engine
from models import User, Asset, Portfolio  # Assure-toi d'importer tes modèles
from database import Base
from fastapi import FastAPI # type: ignore

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, la base est prête 🐘"}
