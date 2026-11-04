"""
Dimitri System — Backend FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

from routers import voice, chat, files
from services.firebase_admin import init_firebase

try:
    from routers import whatsapp
    _has_wa = True
except Exception as e:
    print(f"[WARN] whatsapp router no cargado: {e}")
    _has_wa = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando Dimitri System Backend...")
    print("GROQ_API_KEY set:", bool((os.getenv("GROQ_API_KEY") or "").strip()))
    try:
        init_firebase()
    except Exception as e:
        print(f"[WARN] init_firebase: {e}")
    print("Dimitri listo.")
    yield
    print("Backend detenido.")


app = FastAPI(
    title="Dimitri System API",
    description="Backend adaptativo · Voz + Chat + Entregables",
    version="2.0.2",
    lifespan=lifespan,
)

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
if _has_wa:
    app.include_router(whatsapp.router)


@app.get("/")
async def root():
    return {
        "message": "Dimitri System Backend activo",
        "philosophy": "Cero respuestas negativas",
        "docs": "/docs",
        "version": "2.0.2",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "groq": bool((os.getenv("GROQ_API_KEY") or "").strip()),
        "version": "2.0.2",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
