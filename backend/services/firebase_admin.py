import os
from typing import Dict, Any, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv

load_dotenv()

_db = None
_initialized = False


def init_firebase():
    global _db, _initialized
    if _initialized:
        return
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    # En Render a veces el archivo está en /etc/secrets/ o la raíz del servicio
    candidates = [
        cred_path,
        os.path.join(os.getcwd(), "serviceAccountKey.json"),
        "/etc/secrets/serviceAccountKey.json",
        "backend/serviceAccountKey.json",
    ]
    try:
        cred = None
        used = None
        for p in candidates:
            if p and os.path.exists(p):
                cred = credentials.Certificate(p)
                used = p
                break
        if cred is not None:
            opts = {}
            bucket = os.getenv("FIREBASE_STORAGE_BUCKET")
            if bucket:
                opts["storageBucket"] = bucket
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, opts or None)
            _db = firestore.client()
            print(f"[OK] Firebase Admin inicializado ({used}).")
        else:
            print(f"[WARN] No se encontró serviceAccountKey.json. Rutas probadas: {candidates}")
            _db = None
    except Exception as e:
        print(f"[WARN] Firebase no inicializado ({e}). Modo simulación activo.")
        _db = None
    _initialized = True


def get_db():
    if not _initialized:
        init_firebase()
    return _db


async def save_deliverable(uid: str, data: Dict[str, Any]) -> str:
    db = get_db()
    task_id = data.get("task_id") or data.get("id") or ("sim-" + datetime.utcnow().isoformat())
    if db is None:
        return task_id
    try:
        doc_ref = db.collection("users").document(uid).collection("deliverables").document()
        payload = {**data, "createdAt": firestore.SERVER_TIMESTAMP, "status": "ready"}
        doc_ref.set(payload)
        return doc_ref.id
    except Exception as e:
        print(f"[WARN] save_deliverable: {e}")
        return task_id


async def update_status(uid: str, state: str, message: Optional[str] = None, expression: Optional[str] = None):
    db = get_db()
    if db is None:
        return
    try:
        db.collection("users").document(uid).collection("status").document("current").set({
            "state": state,
            "message": message,
            "expression": expression,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        }, merge=True)
    except Exception as e:
        print(f"[WARN] update_status: {e}")


async def append_chat_message(uid: str, session_id: str, role: str, content: str, meta: Optional[Dict] = None):
    db = get_db()
    if db is None:
        return
    try:
        db.collection("users").document(uid).collection("sessions").document(session_id)\
            .collection("messages").add({
                "role": role,
                "content": content,
                "meta": meta or {},
                "createdAt": firestore.SERVER_TIMESTAMP,
            })
    except Exception as e:
        print(f"[WARN] append_chat_message: {e}")


async def verify_id_token(id_token: str) -> Optional[str]:
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded["uid"]
    except Exception:
        return None
