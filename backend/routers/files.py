from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter(prefix="/api/v1/files", tags=["files"])
DELIVERABLES_DIR = Path("deliverables")
DELIVERABLES_DIR.mkdir(exist_ok=True)


@router.get("/download/{filename:path}")
async def download_file(filename: str):
    if ".." in filename:
        raise HTTPException(status_code=400, detail="Nombre inválido")
    # filename puede venir como uid_nombre.xlsx
    path = DELIVERABLES_DIR / filename
    if not path.exists():
        matches = list(DELIVERABLES_DIR.glob(f"*{filename}"))
        if not matches:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        path = matches[0]
    return FileResponse(path, filename=path.name.split("_", 1)[-1] if "_" in path.name else path.name)
