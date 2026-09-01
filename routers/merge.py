import asyncio
import uuid

from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pypdf import PdfWriter
from typing import List
from core.config import MAX_FILE_SIZE

router = APIRouter()

TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)


@router.post("/")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Upload at least 2 PDF files to merge")


    writer = PdfWriter()
    saved_paths = []

    try:
        for f in files:
            if f.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail=f"{f.filename} is not a PDF")

            content = await f.read()

            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail=f"{f.filename} is too large. Max size is 100MB.")

            temp_path = TEMP_DIR / f"{uuid.uuid4()}_input.pdf"
            temp_path.write_bytes(content)
            saved_paths.append(temp_path)
            await asyncio.to_thread(writer.append, str(temp_path))

        def write_merged():
            output_name = f"merged_{uuid.uuid4().hex[:8]}.pdf"
            output_path = TEMP_DIR / output_name
            with open(output_path, "wb") as out:
                writer.write(out)
            writer.close()
            return output_path

        output_path = await asyncio.to_thread(write_merged)

        return FileResponse(
            path=output_path,
            filename="merged.pdf",
            media_type="application/pdf",
        )

    finally:
        for p in saved_paths:
            p.unlink(missing_ok=True)