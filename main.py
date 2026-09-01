import asyncio
import contextlib
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    compress,
    excel_to_pdf,
    jpg_to_pdf,
    merge,
    pdf_to_excel,
    pdf_to_jpg,
    pdf_to_ppt,
    pdf_to_word,
    ppt_to_pdf,
    split,
    word_to_pdf,
)
from core.cleanup import sweeper_loop
from core.ratelimit import RateLimitMiddleware

app = FastAPI(title="DamnPDF API")

# Comma-separated list, e.g. CORS_ORIGINS="https://damnpdf.vercel.app,https://custom.domain"
default_origins = "http://localhost:5173,http://127.0.0.1:5173"
allowed_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", default_origins).split(",") if o.strip()]

app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(merge.router, prefix="/api/merge", tags=["merge"])
app.include_router(split.router, prefix="/api/split", tags=["split"])
app.include_router(compress.router, prefix="/api/compress", tags=["compress"])
app.include_router(jpg_to_pdf.router, prefix="/api/convert", tags=["convert"])
app.include_router(pdf_to_jpg.router, prefix="/api/convert", tags=["convert"])
app.include_router(word_to_pdf.router, prefix="/api/convert", tags=["convert"])
app.include_router(ppt_to_pdf.router, prefix="/api/convert", tags=["convert"])
app.include_router(excel_to_pdf.router, prefix="/api/convert", tags=["convert"])
app.include_router(pdf_to_word.router, prefix="/api/convert", tags=["convert"])
app.include_router(pdf_to_ppt.router, prefix="/api/convert", tags=["convert"])
app.include_router(pdf_to_excel.router, prefix="/api/convert", tags=["convert"])


@app.on_event("startup")
async def start_sweeper():
    app.state.sweeper = asyncio.create_task(sweeper_loop())


@app.on_event("shutdown")
async def stop_sweeper():
    task = getattr(app.state, "sweeper", None)
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


@app.get("/")
def health():
    return {"status": "DamnPDF API running"}
