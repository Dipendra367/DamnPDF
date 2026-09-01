"""Smoke tests for DamnPDF. Run with the server already up:

    .venv/bin/uvicorn main:app --port 8000 &
    .venv/bin/python test_smoke.py
"""
import io
import os
import sys
import time
import uuid
from pathlib import Path

import httpx
from pypdf import PdfWriter

BASE = os.environ.get("DAMNPDF_URL", "http://localhost:8000")
TEMP_DIR = Path("temp_files")

passed, failed = 0, 0


def check(name: str, ok: bool, detail: str = ""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def make_pdf(pages: int = 2) -> bytes:
    buf = io.BytesIO()
    w = PdfWriter()
    for _ in range(pages):
        w.add_blank_page(width=612, height=792)
    w.write(buf)
    return buf.getvalue()


def make_jpg() -> bytes:
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), (255, 255, 255)).save(buf, "JPEG")
    return buf.getvalue()


def main():
    client = httpx.Client(base_url=BASE, timeout=120)

    print("== health ==")
    r = client.get("/")
    check("health endpoint", r.status_code == 200 and "running" in r.text)

    print("== merge ==")
    pdf = make_pdf()
    r = client.post(
        "/api/merge/",
        files=[
            ("files", ("a.pdf", pdf, "application/pdf")),
            ("files", ("b.pdf", make_pdf(3), "application/pdf")),
        ],
    )
    check("merge 2 PDFs -> 200", r.status_code == 200, f"got {r.status_code}: {r.text[:100]}")
    check("merged output is PDF", r.content[:5] == b"%PDF-")

    r = client.post("/api/merge/", files=[("files", ("a.pdf", pdf, "application/pdf"))])
    check("merge with 1 file -> 400", r.status_code == 400, f"got {r.status_code}")

    print("== split ==")
    r = client.post(
        "/api/split/",
        data={"mode": "range", "ranges": "1"},
        files={"file": ("a.pdf", pdf, "application/pdf")},
    )
    check("split range -> 200", r.status_code == 200, f"got {r.status_code}: {r.text[:100]}")
    r = client.post(
        "/api/split/",
        data={"mode": "bad"},
        files={"file": ("a.pdf", pdf, "application/pdf")},
    )
    check("split bad mode -> 400", r.status_code == 400, f"got {r.status_code}")

    print("== compress ==")
    r = client.post(
        "/api/compress/",
        data={"level": "extreme"},
        files={"file": ("a.pdf", pdf, "application/pdf")},
    )
    check("compress -> 200", r.status_code == 200, f"got {r.status_code}: {r.text[:100]}")
    check("compress returns size headers", "X-Compressed-Size" in r.headers)

    print("== jpg to pdf ==")
    r = client.post(
        "/api/convert/jpg-to-pdf",
        files=[("files", ("x.jpg", make_jpg(), "image/jpeg"))],
    )
    check("jpg-to-pdf -> 200", r.status_code == 200, f"got {r.status_code}: {r.text[:100]}")

    print("== pdf to jpg ==")
    r = client.post(
        "/api/convert/pdf-to-jpg",
        data={"mode": "page"},
        files={"file": ("a.pdf", pdf, "application/pdf")},
    )
    check("pdf-to-jpg -> 200", r.status_code == 200, f"got {r.status_code}: {r.text[:100]}")

    print("== pdf to word (bad pdf must give clean 500) ==")
    r = client.post(
        "/api/convert/pdf-to-word",
        files={"file": ("bad.pdf", b"not a pdf", "application/pdf")},
    )
    check("bad pdf -> 500", r.status_code == 500, f"got {r.status_code}")
    check("no internals leaked in error", "Traceback" not in r.text and "/" not in r.json().get("detail", ""),
          r.text[:200])

    print("== file validation ==")
    r = client.post(
        "/api/convert/pdf-to-word",
        files={"file": ("x.txt", b"hello", "text/plain")},
    )
    check("wrong content type -> 400", r.status_code == 400, f"got {r.status_code}")

    print("== privacy: uuid-only filenames on disk ==")
    # upload with a distinctive marker name, then verify it never lands on disk
    marker = "zzq_mysecret_taxdoc"
    client.post(
        "/api/convert/pdf-to-jpg",
        data={"mode": "page"},
        files={"file": (f"{marker}.pdf", pdf, "application/pdf")},
    )
    leaked = [p.name for p in TEMP_DIR.iterdir() if marker in p.name]
    check("no uploaded filenames stored", not leaked, f"found: {leaked}")

    print("== retention: sweep deletes old files ==")
    stale = TEMP_DIR / f"stale_{uuid.uuid4().hex[:8]}.pdf"
    stale.write_bytes(b"%PDF-1.4 stale")
    old = time.time() - 2 * 3600
    os.utime(stale, (old, old))
    from core.cleanup import sweep_temp_dir
    sweep_temp_dir()
    check("file older than 1h deleted", not stale.exists())

    print("== retention: fresh files kept ==")
    fresh = TEMP_DIR / f"fresh_{uuid.uuid4().hex[:8]}.pdf"
    fresh.write_bytes(b"%PDF-1.4 fresh")
    sweep_temp_dir()
    check("fresh file kept", fresh.exists())
    fresh.unlink(missing_ok=True)

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
