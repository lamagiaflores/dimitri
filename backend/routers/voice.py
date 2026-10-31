from fastapi import APIRouter, Header
from typing import Optional
from models.schemas import VoiceCommand, AdaptiveResponse
from services.adaptive import handle_command
from services.firebase_admin import save_deliverable, update_status

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


@router.post("/command", response_model=AdaptiveResponse)
async def process_voice_command(
    cmd: VoiceCommand,
    authorization: Optional[str] = Header(None),
):
    await update_status(cmd.uid, "thinking", "Procesando tu pedido...", "thinking")

    response = await handle_command(
        transcript=cmd.transcript,
        uid=cmd.uid,
        mode=cmd.mode.value,
        device=cmd.device.value,
    )

    if response.deliverable_created and response.task_id:
        extra = response.extra.get("raw_result", {})
        await save_deliverable(cmd.uid, {
            "id": response.task_id,
            "type": response.deliverable_type or "file",
            "title": extra.get("title", "Entregable Dimitri"),
            "filename": extra.get("filename"),
            "filepath": extra.get("filepath"),
            "origin": "voice",
            "transcript": cmd.transcript,
            "sessionId": cmd.session_id,
            "mode": cmd.mode.value,
        })

    await update_status(cmd.uid, "speaking", response.spoken, response.expression)
    return response


@router.get("/health")
async def health():
    return {"status": "ok", "service": "dimitri-voice"}