import asyncio
import io
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
from core.config import MAX_FILE_SIZE

router = APIRouter()

TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

# A4 at 150 DPI (good balance of quality vs file size)
PAGE_SIZE = (1240, 1754)


def fit_to_page(img: Image.Image) -> Image.Image:
    if img.mode != "RGB":
        img = img.convert("RGB")

    img_ratio = img.width / img.height
    page_ratio = PAGE_SIZE[0] / PAGE_SIZE[1]

    if img_ratio > page_ratio:
        new_width = PAGE_SIZE[0]
        new_height = int(PAGE_SIZE[0] / img_ratio)
    else:
        new_height = PAGE_SIZE[1]
        new_width = int(PAGE_SIZE[1] / img_ratio)

    resized = img.resize((new_width, new_height), Image.LANCZOS)

    page = Image.new("RGB", PAGE_SIZE, (255, 255, 255))
    offset = ((PAGE_SIZE[0] - new_width) // 2, (PAGE_SIZE[1] - new_height) // 2)
    page.paste(resized, offset)

    return page


def build_pdf(contents: list[bytes]) -> Path:
    pages = [fit_to_page(Image.open(io.BytesIO(c))) for c in contents]
    output_path = TEMP_DIR / f"{uuid.uuid4().hex[:8]}_converted.pdf"

    first_page, rest = pages[0], pages[1:]
    first_page.save(
        output_path,
        save_all=True,
        append_images=rest,
        resolution=150.0,
    )
    return output_path


@router.post("/jpg-to-pdf")
async def jpg_to_pdf(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    contents = []

    for f in files:
        if f.content_type not in ("image/jpeg", "image/png", "image/jpg"):
            raise HTTPException(
                status_code=400,
                detail=f"{f.filename} is not a JPG/PNG image",
            )
        content = await f.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"{f.filename} is too large. Max size is 100MB.")

        contents.append(content)

    output_path = await asyncio.to_thread(build_pdf, contents)

    return FileResponse(
        path=output_path,
        filename="converted.pdf",
        media_type="application/pdf",
    )
