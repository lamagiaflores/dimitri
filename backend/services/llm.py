"""
LLM Service — Groq + Function Calling (con timeout para no colgar Render)
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
Eres Dimitri, asistente de IA de alto nivel.
Filosofía OBLIGATORIA: CERO RESPUESTAS NEGATIVAS.
Nunca digas "no puedo", "no sé", "no está disponible" ni equivalentes.
Siempre ofrece una solución, una aproximación útil, un archivo generado o el siguiente paso positivo.
Responde en español natural y profesional.
Si piden Excel, PDF o Word, USA la herramienta correspondiente con datos de ejemplo realistas.
"""

TOOLS: List[Dict] = [
    {
        "type": "function",
        "function": {
            "name": "generate_pdf",
            "description": "Genera un documento PDF profesional.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "filename": {"type": "string"}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_excel",
            "description": "Genera un archivo Excel (.xlsx) con datos tabulares.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "headers": {"type": "array", "items": {"type": "string"}},
                    "rows": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "string"}}
                    },
                    "filename": {"type": "string"}
                },
                "required": ["title", "headers", "rows"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_docx",
            "description": "Genera un documento Word (.docx).",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "filename": {"type": "string"}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_code",
            "description": "Analiza o corrige código.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "language": {"type": "string"},
                    "task": {"type": "string"}
                },
                "required": ["code", "task"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Guarda una nota personal.",
            "parameters": {
                "type": "object",
                "properties": {"note": {"type": "string"}},
                "required": ["note"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "general_answer",
            "description": "Responde de forma útil.",
            "parameters": {
                "type": "object",
                "properties": {"answer": {"type": "string"}},
                "required": ["answer"]
            }
        }
    }
]


def _get_client():
    try:
        from groq import Groq
        key = (os.getenv("GROQ_API_KEY") or "").strip()
        if not key:
            return None
        # timeout evita que Render se quede colgado
        return Groq(api_key=key, timeout=25.0)
    except Exception as e:
        print(f"[WARN] Groq client: {e}")
        return None


def _heuristic_action(transcript: str) -> Dict[str, Any]:
    t = (transcript or "").lower()
    if re.search(r"excel|xlsx|hoja de c[aá]lculo|reporte|abarrotes|ventas", t):
        return {
            "action": "generate_excel",
            "args": {
                "title": "Reporte de tienda de abarrotes",
                "headers": ["Producto", "Categoría", "Stock", "Precio unitario", "Ventas del día"],
                "rows": [
                    ["Arroz 1kg", "Abarrotes", "40", "4.50", "12"],
                    ["Aceite 1L", "Abarrotes", "25", "9.90", "8"],
                    ["Leche 1L", "Lácteos", "30", "4.20", "15"],
                    ["Pan francés", "Panadería", "50", "0.30", "40"],
                    ["Huevos x12", "Fresco", "18", "8.50", "6"],
                ],
                "filename": "reporte_abarrotes.xlsx",
            },
        }
    if re.search(r"\bpdf\b|informe", t):
        return {
            "action": "generate_pdf",
            "args": {
                "title": "Informe Dimitri",
                "content": f"Informe generado a partir de:\n\n{transcript}",
                "filename": "informe_dimitri.pdf",
            },
        }
    if re.search(r"\bword\b|\bdocx\b", t):
        return {
            "action": "generate_docx",
            "args": {
                "title": "Documento Dimitri",
                "content": f"Documento generado:\n\n{transcript}",
                "filename": "documento_dimitri.docx",
            },
        }
    return {
        "action": "general_answer",
        "args": {
            "answer": f"Entendido: «{(transcript or '')[:200]}». "
                      f"Puedo generar Excel, PDF o Word si me lo pides."
        },
    }


async def process_with_llm(
    transcript: str,
    mode: str = "personal",
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    # Atajo local: si pide excel/pdf/word, no dependemos de Groq (rápido y fiable en Render free)
    tlow = (transcript or "").lower()
    if re.search(r"excel|xlsx|pdf|\bword\b|docx|reporte|abarrotes", tlow):
        print("[INFO] Atajo local de generación de archivo")
        return _heuristic_action(transcript)

    mode_hint = (
        "MODO EMPRESARIAL."
        if mode == "business"
        else "MODO PERSONAL."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n" + mode_hint},
        {"role": "user", "content": f"Mensaje del usuario:\n{transcript}"},
    ]

    client = _get_client()
    if client is None:
        print("[WARN] Sin GROQ_API_KEY — heurística")
        return _heuristic_action(transcript)

    try:
        import asyncio
        loop = asyncio.get_event_loop()

        def _call():
            return client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.35,
                max_tokens=1200,
            )

        response = await asyncio.wait_for(loop.run_in_executor(None, _call), timeout=28)
        message = response.choices[0].message
        if getattr(message, "tool_calls", None):
            tc = message.tool_calls[0]
            args = json.loads(tc.function.arguments)
            return {"action": tc.function.name, "args": args, "raw": message.content}
        content = message.content or "Listo, aquí tienes una respuesta útil."
        return {"action": "general_answer", "args": {"answer": content}, "raw": content}
    except Exception as e:
        print(f"[WARN] Groq/timeout: {e}")
        return _heuristic_action(transcript)
