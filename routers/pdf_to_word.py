import asyncio
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pdf2docx import Converter

from core.office_convert import TEMP_DIR
from core.config import MAX_FILE_SIZE
from core.limits import conversion_semaphore

router = APIRouter()


@router.post("/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max size is 100MB.")

    job_id = uuid.uuid4().hex[:8]
    input_path = TEMP_DIR / f"{job_id}_input.pdf"
    output_path = TEMP_DIR / f"{job_id}_output.docx"
    input_path.write_bytes(content)

    def run_conversion():
        cv = Converter(str(input_path))
        cv.convert(str(output_path))
        cv.close()

    try:
        async with conversion_semaphore:
            await asyncio.to_thread(run_conversion)

        if not output_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Conversion completed but output file not found",
            )

        return FileResponse(
            path=output_path,
            filename="converted.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="PDF to Word conversion failed")
    finally:
        input_path.unlink(missing_ok=True)