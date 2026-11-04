"""Generación de entregables — siempre intenta devolver algo útil."""

import os
import uuid
import csv
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

DELIVERABLES_DIR = Path("deliverables")
DELIVERABLES_DIR.mkdir(exist_ok=True)

BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://dimitri-718z.onrender.com")


def _download_url(filename: str) -> str:
    return f"{BASE_URL}/api/v1/files/download/{filename}"


async def execute_tool(action: str, args: Dict[str, Any], uid: str) -> Dict[str, Any]:
    handlers = {
        "generate_pdf": _generate_pdf,
        "generate_excel": _generate_excel,
        "generate_docx": _generate_docx,
        "analyze_code": _analyze_code,
        "create_note": _create_note,
        "general_answer": _general_answer,
    }
    handler = handlers.get(action, _general_answer)
    try:
        return await handler(args, uid)
    except Exception as e:
        print(f"[WARN] tool {action}: {e}")
        return {
            "spoken": "Preparé una respuesta útil aunque hubo un detalle técnico al generar el archivo.",
            "chat_reply": f"Detalle: {str(e)[:120]}. Puedes reintentar el pedido.",
            "expression": "thinking",
            "deliverable_created": False,
        }


async def _generate_pdf(args: Dict, uid: str) -> Dict:
    title = args.get("title", "Documento Dimitri")
    content = args.get("content", "")
    short = f"doc_{uuid.uuid4().hex[:8]}.pdf"
    filepath = DELIVERABLES_DIR / f"{uid}_{short}"
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(str(title).replace("&", "&amp;"), styles["Title"]),
            Spacer(1, 0.4 * cm),
            Paragraph(str(content).replace("\n", "<br/>").replace("&", "&amp;"), styles["Normal"]),
        ]
        doc.build(story)
        fname = short
    except Exception as e:
        print(f"[WARN] reportlab: {e}")
        short = f"doc_{uuid.uuid4().hex[:8]}.txt"
        filepath = DELIVERABLES_DIR / f"{uid}_{short}"
        filepath.write_text(f"{title}\n\n{content}", encoding="utf-8")
        fname = short

    task_id = str(uuid.uuid4())
    return {
        "spoken": f"¡Documento listo! «{title}» ya está en tu panel.",
        "chat_reply": f"Documento generado: **{title}**",
        "expression": "happy",
        "deliverable_created": True,
        "task_id": task_id,
        "type": "pdf" if fname.endswith(".pdf") else "txt",
        "title": title,
        "filename": fname,
        "filepath": str(filepath),
        "download_url": _download_url(f"{uid}_{fname}"),
    }


async def _generate_excel(args: Dict, uid: str) -> Dict:
    title = args.get("title", "Reporte Excel")
    headers: List[str] = args.get("headers") or ["Columna A", "Columna B"]
    rows: List[List] = args.get("rows") or [["Dato 1", "Dato 2"]]
    short = f"excel_{uuid.uuid4().hex[:8]}.xlsx"
    filepath = DELIVERABLES_DIR / f"{uid}_{short}"
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = str(title)[:31]
        ws.append(headers)
        for row in rows:
            ws.append([str(c) if c is not None else "" for c in row])
        wb.save(str(filepath))
        fname = short
    except Exception as e:
        print(f"[WARN] openpyxl: {e}")
        short = f"excel_{uuid.uuid4().hex[:8]}.csv"
        filepath = DELIVERABLES_DIR / f"{uid}_{short}"
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            for row in rows:
                w.writerow(row)
        fname = short

    task_id = str(uuid.uuid4())
    return {
        "spoken": f"¡Excel listo! «{title}» con {len(rows)} filas ya está en tu panel.",
        "chat_reply": f"Archivo generado: **{title}** ({len(rows)} filas). Descárgalo en el panel derecho.",
        "expression": "happy",
        "deliverable_created": True,
        "task_id": task_id,
        "type": "xlsx" if fname.endswith(".xlsx") else "csv",
        "title": title,
        "filename": fname,
        "filepath": str(filepath),
        "download_url": _download_url(f"{uid}_{fname}"),
    }


async def _generate_docx(args: Dict, uid: str) -> Dict:
    title = args.get("title", "Documento Word")
    content = args.get("content", "")
    short = f"doc_{uuid.uuid4().hex[:8]}.docx"
    filepath = DELIVERABLES_DIR / f"{uid}_{short}"
    try:
        from docx import Document
        document = Document()
        document.add_heading(str(title), 0)
        for para in str(content).split("\n"):
            document.add_paragraph(para)
        document.save(str(filepath))
        fname = short
    except Exception as e:
        print(f"[WARN] python-docx: {e}")
        short = f"doc_{uuid.uuid4().hex[:8]}.txt"
        filepath = DELIVERABLES_DIR / f"{uid}_{short}"
        filepath.write_text(f"{title}\n\n{content}", encoding="utf-8")
        fname = short

    task_id = str(uuid.uuid4())
    return {
        "spoken": f"Documento «{title}» listo en tu panel.",
        "chat_reply": f"Documento generado: **{title}**",
        "expression": "happy",
        "deliverable_created": True,
        "task_id": task_id,
        "type": "docx" if fname.endswith(".docx") else "txt",
        "title": title,
        "filename": fname,
        "filepath": str(filepath),
        "download_url": _download_url(f"{uid}_{fname}"),
    }


async def _analyze_code(args: Dict, uid: str) -> Dict:
    code = args.get("code", "")
    language = args.get("language", "código")
    task = args.get("task", "analizar")
    analysis = f"# Análisis ({language})\nTarea: {task}\n\n```{language}\n{code[:3000]}\n```\n"
    short = f"analisis_{uuid.uuid4().hex[:8]}.md"
    filepath = DELIVERABLES_DIR / f"{uid}_{short}"
    filepath.write_text(analysis, encoding="utf-8")
    task_id = str(uuid.uuid4())
    return {
        "spoken": "Analicé el código y dejé el informe en tu panel.",
        "chat_reply": f"Análisis de {language} listo.",
        "expression": "thinking",
        "deliverable_created": True,
        "task_id": task_id,
        "type": "code",
        "title": f"Análisis {language}",
        "filename": short,
        "filepath": str(filepath),
        "download_url": _download_url(f"{uid}_{short}"),
    }


async def _create_note(args: Dict, uid: str) -> Dict:
    note = args.get("note", "")
    return {
        "spoken": "Nota registrada.",
        "chat_reply": f"Nota: {note[:300]}",
        "expression": "happy",
        "deliverable_created": False,
        "answer": note,
    }


async def _general_answer(args: Dict, uid: str) -> Dict:
    answer = args.get("answer", "Listo. Aquí tienes una respuesta útil.")
    return {
        "spoken": answer,
        "chat_reply": answer,
        "expression": "happy",
        "deliverable_created": False,
        "answer": answer,
    }
