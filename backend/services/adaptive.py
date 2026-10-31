from typing import Dict, Any, Optional
from services.llm import process_with_llm
from services.tools import execute_tool
from models.schemas import AdaptiveResponse
from datetime import datetime


async def handle_command(
    transcript: str,
    uid: str,
    mode: str = "personal",
    device: str = "mobile",
    context: Optional[Dict] = None,
) -> AdaptiveResponse:
    decision = await process_with_llm(transcript, mode=mode, context=context)
    action = decision.get("action", "general_answer")
    args = decision.get("args", {})

    result = await execute_tool(action, args, uid=uid)

    spoken = result.get("spoken") or _positive_fallback(action, result)
    chat_reply = result.get("chat_reply") or spoken

    return AdaptiveResponse(
        spoken=spoken,
        expression=result.get("expression", "happy"),
        chat_reply=chat_reply,
        task_id=result.get("task_id"),
        deliverable_created=result.get("deliverable_created", False),
        deliverable_type=result.get("type"),
        download_url=result.get("download_url"),
        extra={
            "action": action,
            "raw_result": {k: v for k, v in result.items() if k not in ("spoken",)},
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


def _positive_fallback(action: str, result: Dict) -> str:
    templates = {
        "generate_pdf": "¡Documento PDF listo en tu panel!",
        "generate_excel": "¡Excel generado y disponible en tu panel!",
        "generate_docx": "¡Documento Word listo en tu panel!",
        "analyze_code": "Análisis de código listo en tu panel.",
        "create_note": "Nota guardada correctamente.",
        "general_answer": result.get("answer", "Entendido. Aquí tienes la mejor respuesta posible."),
    }
    return templates.get(action, "Listo. Ya trabajé en eso y te dejo el resultado preparado.")