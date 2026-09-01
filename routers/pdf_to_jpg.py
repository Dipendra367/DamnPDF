import asyncio
import uuid
import zipfile
from pathlib import Path

import pymupdf
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from pdf2image import convert_from_path
from core.config import MAX_FILE_SIZE
from core.limits import conversion_semaphore

router = APIRouter()

TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)


def zip_images(image_paths: list[Path], zip_path: Path):
    with zipfile.ZipFile(zip_path, "w") as zf:
        for img_path in image_paths:
            zf.write(img_path, arcname=img_path.name)


def convert(input_path: Path, output_dir: Path, zip_path: Path, mode: str) -> Path:
    """Blocking worker: renders pages or extracts images, returns the file to serve."""
    image_paths = []

    if mode == "page":
        pages = convert_from_path(input_path, dpi=150)
        if not pages:
            raise HTTPException(status_code=500, detail="No pages found in PDF")

        for i, page in enumerate(pages, start=1):
            img_path = output_dir / f"page_{i}.jpg"
            page.save(img_path, "JPEG", quality=90)
            image_paths.append(img_path)

    else:  # extract
        doc = pymupdf.open(input_path)
        count = 0
        for page_index in range(len(doc)):
            for img in doc.get_page_images(page_index):
                xref = img[0]
                base_image = doc.extract_image(xref)
                img_bytes = base_image["image"]
                ext = base_image["ext"]
                count += 1
                img_path = output_dir / f"image_{count}.{ext}"
                img_path.write_bytes(img_bytes)
                image_paths.append(img_path)
        doc.close()

        if not image_paths:
            raise HTTPException(
                status_code=404,
                detail="No embedded images found in this PDF",
            )

    if len(image_paths) == 1:
        return image_paths[0]

    zip_images(image_paths, zip_path)
    return zip_path


@router.post("/pdf-to-jpg")
async def pdf_to_jpg(
    file: UploadFile = File(...),
    mode: str = Form("page"),  # "page" or "extract"
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    if mode not in ("page", "extract"):
        raise HTTPException(status_code=400, detail="mode must be 'page' or 'extract'")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max size is 100MB.")

    job_id = uuid.uuid4().hex[:8]
    input_path = TEMP_DIR / f"{job_id}_input.pdf"
    output_dir = TEMP_DIR / f"{job_id}_pages"
    output_dir.mkdir(exist_ok=True)
    input_path.write_bytes(content)
    zip_path = TEMP_DIR / f"{job_id}_converted.zip"

    try:
        async with conversion_semaphore:
            result_path = await asyncio.to_thread(convert, input_path, output_dir, zip_path, mode)

        if result_path.suffix == ".jpg":
            return FileResponse(path=result_path, filename="converted.jpg", media_type="image/jpeg")
        return FileResponse(path=result_path, filename="converted.zip", media_type="application/zip")
    finally:
        input_path.unlink(missing_ok=True)
