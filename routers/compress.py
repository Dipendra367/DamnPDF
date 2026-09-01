import asyncio
import logging
import subprocess
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from core.config import MAX_FILE_SIZE
from core.limits import conversion_semaphore

logger = logging.getLogger("damnpdf.compress")

router = APIRouter()

TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

PRESET_MAP = {
    "extreme": "/screen",
    "recommended": "/ebook",
    "less": "/printer",
}


@router.post("/")
async def compress_pdf(
    file: UploadFile = File(...),
    level: str = Form("recommended"),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max size is 100MB.")

    if level not in PRESET_MAP:
        raise HTTPException(
            status_code=400,
            detail="level must be 'extreme', 'recommended', or 'less'",
        )

    input_path = TEMP_DIR / f"{uuid.uuid4()}_input.pdf"
    output_path = TEMP_DIR / f"{uuid.uuid4()}_output.pdf"
    input_path.write_bytes(content)

    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={PRESET_MAP[level]}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]

    try:
        async with conversion_semaphore:
            result = await asyncio.to_thread(
                subprocess.run,
                gs_command,
                capture_output=True,
                text=True,
                timeout=60,
            )

        if result.returncode != 0 or not output_path.exists():
            logger.warning("Ghostscript failed (code %s): %s", result.returncode, (result.stderr or "")[:500])
            raise HTTPException(
                status_code=500,
                detail="Compression failed. This PDF may be corrupted or use unsupported features.",
            )

        original_size = len(content)
        compressed_size = output_path.stat().st_size

        return FileResponse(
            path=output_path,
            filename="compressed.pdf",
            media_type="application/pdf",
            headers={
                "X-Original-Size": str(original_size),
                "X-Compressed-Size": str(compressed_size),
            },
        )
    finally:
        input_path.unlink(missing_ok=True)