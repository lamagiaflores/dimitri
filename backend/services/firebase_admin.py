import os
from typing import Dict, Any, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from dotenv import load_dotenv

load_dotenv()

_db = None
_bucket = None
_initialized = False


def init_firebase():
    global _db, _bucket, _initialized
    if _initialized:
        return
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    try:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")
            } if os.getenv("FIREBASE_STORAGE_BUCKET") else None)
        else:
            firebase_admin.initialize_app()
        _db = firestore.client()
        try:
            _bucket = storage.bucket()
        except Exception:
            _bucket = None
        print("[OK] Firebase Admin inicializado.")
    except Exception as e:
        print(f"[WARN] Firebase no inicializado ({e}). Modo simulación activo.")
    _initialized = True


def get_db():
    if not _initialized:
        init_firebase()
    return _db


async def save_deliverable(uid: str, data: Dict[str, Any]) -> str:
    db = get_db()
    if db is None:
        return data.get("task_id", "sim-" + datetime.utcnow().isoformat())
    doc_ref = db.collection("users").document(uid).collection("deliverables").document()
    payload = {**data, "createdAt": firestore.SERVER_TIMESTAMP, "status": "ready"}
    doc_ref.set(payload)
    return doc_ref.id


async def update_status(uid: str, state: str, message: Optional[str] = None, expression: Optional[str] = None):
    db = get_db()
    if db is None:
        return
    db.collection("users").document(uid).collection("status").document("current").set({
        "state": state,
        "message": message,
        "expression": expression,
        "updatedAt": firestore.SERVER_TIMESTAMP,
    }, merge=True)


async def append_chat_message(uid: str, session_id: str, role: str, content: str, meta: Optional[Dict] = None):
    db = get_db()
    if db is None:
        return
    db.collection("users").document(uid).collection("sessions").document(session_id)\
        .collection("messages").add({
            "role": role,
            "content": content,
            "meta": meta or {},
            "createdAt": firestore.SERVER_TIMESTAMP,
        })


async def verify_id_token(id_token: str) -> Optional[str]:
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded["uid"]
    except Exception:
        return None