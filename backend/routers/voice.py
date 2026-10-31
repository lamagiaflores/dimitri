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
    try:
        try:
            await update_status(cmd.uid, "thinking", "Procesando tu pedido...", "thinking")
        except Exception:
            pass

        mode = cmd.mode.value if hasattr(cmd.mode, "value") else str(cmd.mode or "personal")
        device = cmd.device.value if hasattr(cmd.device, "value") else str(cmd.device or "mobile")

        response = await handle_command(
            transcript=cmd.transcript,
            uid=cmd.uid,
            mode=mode,
            device=device,
        )

        if response.deliverable_created and response.task_id:
            extra = response.extra.get("raw_result", {})
            try:
                await save_deliverable(cmd.uid, {
                    "id": response.task_id,
                    "type": response.deliverable_type or "file",
                    "title": extra.get("title", "Entregable Dimitri"),
                    "filename": extra.get("filename"),
                    "filepath": extra.get("filepath"),
                    "origin": "voice",
                    "transcript": cmd.transcript,
                    "sessionId": cmd.session_id,
                    "mode": mode,
                })
            except Exception as e:
                print(f"[WARN] save_deliverable voice: {e}")

        try:
            await update_status(cmd.uid, "speaking", response.spoken, response.expression)
        except Exception:
            pass
        return response
    except Exception as e:
        print(f"[ERROR] voice/command: {e}")
        return AdaptiveResponse(
            spoken="Recibí tu pedido y lo estoy resolviendo de otra forma. Inténtalo de nuevo.",
            expression="thinking",
            chat_reply=str(e)[:120],
            deliverable_created=False,
        )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "dimitri-voice"}
