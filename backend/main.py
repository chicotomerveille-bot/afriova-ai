from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Afriova AI Backend...")
    yield
    # Shutdown
    print("🛑 Shutting down Afriova AI Backend...")

app = FastAPI(
    title="Afriova AI API",
    description="API pour les agents IA autonomes adaptés au marché africain",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API d'Afriova AI",
        "version": "0.1.0",
        "status": "operational",
        "agents_available": [
            "amara (Téléphonique)",
            "kofi (Marketing)",
            "amina (Assistante)",
            "tendai (SEO)",
            "jafari (Commercial)",
            "sadiq (Comptable)",
            "ife (Juridique)",
            "rayan (RH)"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2026-10-05T17:30:00Z"}

@app.get("/agents")
async def list_agents():
    return {
        "agents": [
            {
                "id": "amara",
                "name": "Amara",
                "role": "Agent Téléphonique & SAV",
                "description": "Gestion des appels 24/7, qualification, prise de RDV, SAV sur WhatsApp/SMS"
            },
            {
                "id": "kofi",
                "name": "Kofi",
                "role": "Agent Marketing & Social Media",
                "description": "Création de visuels, rédaction de posts, publication multi-plateformes, calendrier éditorial"
            },
            {
                "id": "amina",
                "name": "Amina",
                "role": "Agent Général / Assistante IA",
                "description": "Bras droit digital : to-do list, gestion d'équipe IA, exécution via WhatsApp"
            }
            # More agents can be added
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )