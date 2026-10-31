from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter(prefix="/api/v1/files", tags=["files"])

DELIVERABLES_DIR = Path("deliverables")


@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Descarga un entregable generado.
    En producción preferir URLs firmadas de Firebase Storage.
    """
    # Seguridad básica: solo nombres de archivo simples
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    path = DELIVERABLES_DIR / filename
    if not path.exists():
        # intentar con cualquier prefijo uid_
        matches = list(DELIVERABLES_DIR.glob(f"*_{filename}"))
        if not matches:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        path = matches[0]
    return FileResponse(path, filename=path.name)