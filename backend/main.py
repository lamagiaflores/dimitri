"""
Dimitri System — Backend FastAPI
Cerebro central con filosofía de cero respuestas negativas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import voice, chat, files
from services.firebase_admin import init_firebase
import os
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando Dimitri System Backend...")
    init_firebase()
    print("✅ Dimitri listo. Filosofía: cero respuestas negativas.")
    yield
    print("👋 Backend detenido.")


app = FastAPI(
    title="Dimitri System API",
    description="Backend adaptativo · Voz + Chat + Entregables · Cero negativas",
    version="2.0.0",
    lifespan=lifespan,
)

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(chat.router)
app.include_router(files.router)


@app.get("/")
async def root():
    return {
        "message": "Dimitri System Backend activo",
        "philosophy": "Cero respuestas negativas",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)