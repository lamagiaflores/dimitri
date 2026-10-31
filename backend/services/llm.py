"""
LLM Service — Groq + Function Calling
Filosofía: siempre produce una acción o respuesta útil.
"""

import os
import json
from typing import Dict, Any, Optional, List
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
Eres Dimitri, asistente de IA de alto nivel.
Filosofía OBLIGATORIA: CERO RESPUESTAS NEGATIVAS.
Nunca digas "no puedo", "no sé", "no está disponible" ni equivalentes.
Siempre ofrece una solución, una aproximación útil, un archivo generado o el siguiente paso positivo.
Responde en español natural y profesional.
Cuando uses herramientas, elige la más adecuada según el perfil del usuario (personal o empresarial).
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
                    "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
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
            "description": "Analiza o corrige código y genera un archivo con el resultado.",
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
            "description": "Guarda una nota personal del usuario.",
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
            "description": "Responde cualquier pregunta de forma útil y creativa.",
            "parameters": {
                "type": "object",
                "properties": {"answer": {"type": "string"}},
                "required": ["answer"]
            }
        }
    }
]


async def process_with_llm(
    transcript: str,
    mode: str = "personal",
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    mode_hint = (
        "El usuario está en MODO EMPRESARIAL (inventario, reportes, mostrador, WhatsApp)."
        if mode == "business"
        else "El usuario está en MODO PERSONAL (música, notas, consultas diarias)."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n" + mode_hint},
        {"role": "user", "content": f"Comando / mensaje del usuario:\n{transcript}"}
    ]
    if context:
        messages.insert(1, {"role": "system", "content": f"Contexto: {json.dumps(context, ensure_ascii=False)}"})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.35,
            max_tokens=1500,
        )
        message = response.choices[0].message
        if message.tool_calls:
            tc = message.tool_calls[0]
            return {
                "action": tc.function.name,
                "args": json.loads(tc.function.arguments),
                "raw": message.content
            }
        return {
            "action": "general_answer",
            "args": {"answer": message.content or "Entendido. Aquí tienes la mejor respuesta posible ahora mismo."},
            "raw": message.content
        }
    except Exception as e:
        return {
            "action": "general_answer",
            "args": {
                "answer": f"Estoy procesando tu pedido de forma creativa. Recibí: {transcript[:100]}..."
            },
            "error": str(e)
        }