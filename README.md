# DamnPDF

A fast, self-hostable PDF toolkit. Merge, split, compress, and convert PDFs to/from Word, PowerPoint, Excel, and images — with no accounts, no tracking, and files that are deleted automatically within an hour.

**The pitch:** most online PDF tools ask you to trust a black box. DamnPDF is open source, stores your files under random IDs, deletes everything automatically, and if that's still not enough — run it yourself.

## Tools

| | Tool | What it does |
|---|---|---|
| Organize | **Merge PDF** | Combine multiple PDFs into one |
| Organize | **Split PDF** | Extract page ranges, or split into one PDF per page (zip) |
| Optimize | **Compress PDF** | Shrink PDFs with Ghostscript (3 quality presets) |
| Convert | **PDF → Word** | Editable DOCX via pdf2docx |
| Convert | **PDF → PowerPoint** | Real PPTX slides (page renders) via python-pptx |
| Convert | **PDF → Excel** | Tables, text, and images into XLSX sheets |
| Convert | **Word → PDF** | LibreOffice |
| Convert | **PowerPoint → PDF** | LibreOffice |
| Convert | **Excel → PDF** | LibreOffice |
| Convert | **PDF → JPG** | Render pages as images, or extract embedded images |
| Convert | **JPG → PDF** | Images into an A4 PDF (processed fully in memory) |

## Privacy model

- **Anonymous.** No accounts, no email, no analytics, no tracking. The server never knows who you are.
- **Ephemeral.** Input files are deleted the moment your conversion finishes. Output files are kept for at most **1 hour** (so a failed download can be retried), then deleted by an automated sweeper that runs every 15 minutes.
- **Random names.** Files are stored under random UUIDs — never their original filenames.
- **Verifiable.** The retention logic is a few lines of Python (`core/cleanup.py`) you can read yourself.
- **Self-hostable.** One Docker image runs the whole thing (see below), so the only person who can see your files is you.

Read the full policy at the `/privacy` page in the frontend.

## Architecture

```
DamnPDF/
├── main.py              # FastAPI app, CORS, rate limit, cleanup task
├── core/
│   ├── cleanup.py       # 1-hour retention sweeper
│   ├── ratelimit.py     # 30 req/min per IP + early 100MB rejection
│   ├── limits.py        # max 3 concurrent heavy conversions (RAM guard)
│   ├── office_convert.py# LibreOffice wrapper (isolated profiles, timeouts)
│   └── config.py        # all tunables (file size, retention, limits)
├── routers/             # 11 endpoints, one file per tool
├── frontend/            # React + Vite SPA
└── Dockerfile           # python:3.12-slim + LibreOffice + Ghostscript + poppler
```

Engines: [pypdf](https://github.com/py-pdf/pypdf), [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx), [pdfplumber](https://github.com/jsvine/pdfplumber), [PyMuPDF](https://pymupdf.readthedocs.io/), [LibreOffice](https://www.libreoffice.org/), [Ghostscript](https://www.ghostscript.com/), poppler, Pillow.

Heavy work (LibreOffice, Ghostscript, parsing) runs in a threadpool behind a
concurrency cap, so one big conversion never blocks other users, and a burst of
requests can't exhaust RAM.

## Run it locally

**Backend** (needs Python 3.12, LibreOffice, Ghostscript, poppler on PATH):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend** (the dev server proxies `/api` to the backend):

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

## Run it with Docker

One container runs the entire backend, engines included:

```bash
docker build -t damnpdf .
docker run -p 8000:8000 damnpdf
# API at http://localhost:8000, docs at http://localhost:8000/docs
```

Self-hosting the full stack = this container + any static host for `frontend/`
(`npm run build`, then serve `dist/`).

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:5173,...` | Comma-separated allowed frontend origins |
| `VITE_API_URL` | *(empty)* | Frontend build: backend base URL (e.g. `https://api.example.com`) |

Behavior tunables live in `core/config.py`: max file size (100MB), retention
(1 hour), sweep interval (15 min), concurrency cap (3), rate limit (30/min).

## Tests

With the server running:

```bash
pip install httpx   # test dependency
python test_smoke.py
```

16 checks: every endpoint's happy path, validation errors (400/413), clean
error messages (no path/stack leaks), UUID-only filenames on disk, and the
retention sweeper deleting old files while keeping fresh ones.

## License

MIT
