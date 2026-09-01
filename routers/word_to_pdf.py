import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from core.office_convert import convert_with_libreoffice_async, TEMP_DIR
from core.config import MAX_FILE_SIZE

router = APIRouter()


@router.post("/word-to-pdf")
async def word_to_pdf(file: UploadFile = File(...)):
    allowed_types = (
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File must be a Word document")
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max size is 100MB.")


    job_id = uuid.uuid4().hex[:8]
    ext = "docx" if file.filename.endswith(".docx") else "doc"
    input_path = TEMP_DIR / f"{job_id}_input.{ext}"
    input_path.write_bytes(content)

    try:
        output_path = await convert_with_libreoffice_async(input_path, "pdf")

        return FileResponse(
            path=output_path,
            filename="converted.pdf",
            media_type="application/pdf",
        )
    finally:
        input_path.unlink(missing_ok=True)