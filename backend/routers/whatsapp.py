"""
WhatsApp session bridge (esqueleto).

Producción recomendada:
- Evolution API (self-host / cloud) o
- Baileys / whatsapp-web.js en un worker Node

Este router deja los endpoints listos. Mientras no haya bridge real,
devuelve status que el frontend interpreta (y muestra QR demo).
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])

# Memoria temporal (en producción: Redis / Firestore)
_SESSIONS: Dict[str, Dict[str, Any]] = {}


class WaUidBody(BaseModel):
    uid: str


@router.post("/session")
async def create_or_get_session(body: WaUidBody):
    """
    Inicia o recupera sesión WhatsApp para el negocio.
    Cuando el bridge real esté activo, aquí se pide el QR al proveedor.
    """
    uid = body.uid
    existing = _SESSIONS.get(uid)

    if existing and existing.get("status") == "connected":
        return {
            "status": "connected",
            "phone": existing.get("phone"),
            "sessionId": existing.get("sessionId"),
        }

    session_id = str(uuid.uuid4())
    # Placeholder: el bridge real llenaría "qr" con data:image/... o base64
    _SESSIONS[uid] = {
        "sessionId": session_id,
        "status": "waiting_qr",
        "qr": None,  # None → frontend usa QR demo hasta conectar Evolution/Baileys
        "phone": None,
        "updatedAt": datetime.utcnow().isoformat(),
    }

    return {
        "status": "waiting_qr",
        "sessionId": session_id,
        "qr": None,
        "message": (
            "Bridge WhatsApp no configurado aún. "
            "Conecta Evolution API o Baileys y rellena el campo qr."
        ),
    }


@router.get("/status/{uid}")
async def wa_status(uid: str):
    data = _SESSIONS.get(uid) or {"status": "disconnected"}
    return {
        "status": data.get("status", "disconnected"),
        "phone": data.get("phone"),
        "sessionId": data.get("sessionId"),
    }


@router.post("/disconnect")
async def wa_disconnect(body: WaUidBody):
    _SESSIONS.pop(body.uid, None)
    return {"status": "disconnected"}


@router.post("/webhook")
async def wa_webhook(payload: Dict[str, Any]):
    """
    Recibe mensajes entrantes del bridge (Evolution/Baileys).
    Aquí se enganchará Adaptive Engine para responder al cliente.
    """
    # payload típico: { uid, from, text, timestamp }
    # TODO: handle_command + enviar respuesta por el bridge
    return {"ok": True, "received": True}
