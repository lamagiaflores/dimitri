from fastapi import APIRouter, Header
from typing import Optional
from models.schemas import ChatMessage, AdaptiveResponse
from services.adaptive import handle_command
from services.firebase_admin import save_deliverable, update_status, append_chat_message

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/message", response_model=AdaptiveResponse)
async def process_chat_message(
    msg: ChatMessage,
    authorization: Optional[str] = Header(None),
):
    # Construir texto a partir de mensaje + adjuntos
    parts = []
    if msg.text:
        parts.append(msg.text)
    if msg.attachments:
        names = ", ".join(a.get("name", "archivo") for a in msg.attachments)
        parts.append(f"[Archivos adjuntos: {names}]")
    transcript = "\n".join(parts) or "Analiza los archivos adjuntos."

    await update_status(msg.uid, "thinking", "Procesando mensaje...", "thinking")
    await append_chat_message(msg.uid, msg.session_id, "user", transcript)

    response = await handle_command(
        transcript=transcript,
        uid=msg.uid,
        mode=msg.mode.value,
        device="desktop",
        context={"attachments": msg.attachments, "session_id": msg.session_id},
    )

    if response.deliverable_created and response.task_id:
        extra = response.extra.get("raw_result", {})
        await save_deliverable(msg.uid, {
            "id": response.task_id,
            "type": response.deliverable_type or "file",
            "title": extra.get("title", "Entregable Dimitri"),
            "filename": extra.get("filename"),
            "filepath": extra.get("filepath"),
            "origin": "chat",
            "sessionId": msg.session_id,
            "mode": msg.mode.value,
        })

    reply = response.chat_reply or response.spoken
    await append_chat_message(msg.uid, msg.session_id, "assistant", reply, {
        "task_id": response.task_id,
        "deliverable": response.deliverable_created,
    })
    await update_status(msg.uid, "ready", reply, response.expression)
    return response