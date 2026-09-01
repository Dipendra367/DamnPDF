import asyncio
import io
import uuid
import zipfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pypdf import PdfReader, PdfWriter
from core.config import MAX_FILE_SIZE

router = APIRouter()

TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)


def parse_page_ranges(ranges_str: str, total_pages: int) -> list[int]:
    """Parses '1-3,5,7-9' into a sorted list of unique 0-indexed page numbers."""
    pages = set()
    for part in ranges_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-")
            start, end = int(start), int(end)
            if start < 1 or end > total_pages or start > end:
                raise HTTPException(status_code=400, detail=f"Invalid range: {part}")
            pages.update(range(start - 1, end))
        else:
            page = int(part)
            if page < 1 or page > total_pages:
                raise HTTPException(status_code=400, detail=f"Invalid page: {part}")
            pages.add(page - 1)
    return sorted(pages)


@router.post("/")
async def split_pdf(
    file: UploadFile = File(...),
    mode: str = Form(...),  # "range" or "individual"
    ranges: Optional[str] = Form(None),  # required if mode == "range", e.g. "1-3,5,7-9"
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max size is 100MB.")

    reader = await asyncio.to_thread(lambda: PdfReader(io.BytesIO(content)))
    total_pages = len(reader.pages)

    if mode == "range":
        if not ranges:
            raise HTTPException(status_code=400, detail="ranges is required for mode=range")

        page_indices = parse_page_ranges(ranges, total_pages)

        def write_range():
            writer = PdfWriter()
            for idx in page_indices:
                writer.add_page(reader.pages[idx])
            output_name = f"split_{uuid.uuid4().hex[:8]}.pdf"
            output_path = TEMP_DIR / output_name
            with open(output_path, "wb") as out:
                writer.write(out)
            return output_path

        output_path = await asyncio.to_thread(write_range)
        return FileResponse(path=output_path, filename="split.pdf", media_type="application/pdf")

    elif mode == "individual":
        def build_zip():
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for i in range(total_pages):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[i])
                    page_buffer = io.BytesIO()
                    writer.write(page_buffer)
                    zf.writestr(f"page_{i + 1}.pdf", page_buffer.getvalue())
            zip_buffer.seek(0)
            return zip_buffer

        zip_buffer = await asyncio.to_thread(build_zip)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=split_pages.zip"},
        )

    else:
        raise HTTPException(status_code=400, detail="mode must be 'range' or 'individual'")