"""
Dimitri System — Backend FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import voice, chat, files, whatsapp
from services.firebase_admin import init_firebase
import os
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando Dimitri System Backend...")
    print("GROQ_API_KEY set:", bool((os.getenv("GROQ_API_KEY") or "").strip()))
    init_firebase()
    print("Dimitri listo.")
    yield
    print("Backend detenido.")


app = FastAPI(
    title="Dimitri System API",
    description="Backend adaptativo · Voz + Chat + Entregables · Cero negativas",
    version="2.0.1",
    lifespan=lifespan,
)

# CORS abierto para Vercel + local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(chat.router)
app.include_router(files.router)
app.include_router(whatsapp.router)


@app.get("/")
async def root():
    return {
        "message": "Dimitri System Backend activo",
        "philosophy": "Cero respuestas negativas",
        "docs": "/docs",
        "version": "2.0.1",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "groq": bool((os.getenv("GROQ_API_KEY") or "").strip()),
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
