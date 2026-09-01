import asyncio
import logging
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from fastapi import HTTPException

from core.limits import conversion_semaphore

logger = logging.getLogger("damnpdf.office")

TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

MAX_ATTEMPTS = 2  # one retry with a fresh profile: LO crashes are often transient

# Two-stage rescue when direct Office->PDF crashes (a known LO layout bug
# class): round-trip through ODF first, which lays out reliably.
RESCUE_FORMATS = {
    ".doc": "odt", ".docx": "odt", ".rtf": "odt",
    ".ppt": "odp", ".pptx": "odp",
    ".xls": "ods", ".xlsx": "ods",
}


def _attempt(input_path: Path, target_format: str, export_filter: str, output_dir: Path, timeout: int) -> bool:
    """One soffice run with a fresh isolated profile. Returns True on success."""
    convert_target = f"{target_format}:{export_filter}" if export_filter else target_format
    expected_output = output_dir / f"{input_path.stem}.{target_format}"

    # a crashed run leaves a partial output and .~lock files behind; LibreOffice
    # then refuses to overwrite them (Io Abort), so scrub before every attempt
    expected_output.unlink(missing_ok=True)
    (output_dir / f".~lock.{expected_output.name}#").unlink(missing_ok=True)
    (input_path.parent / f".~lock.{input_path.name}#").unlink(missing_ok=True)

    # a fresh, isolated profile per attempt avoids poisoned-profile crashes
    profile_dir = (TEMP_DIR / f"lo_profile_{uuid.uuid4().hex}").resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "soffice",
        "--headless",
        "--nodefault",
        "--norestore",
        "--nolockcheck",
        "--nofirststartwizard",
        f"-env:UserInstallation=file://{profile_dir}",
        "--convert-to", convert_target,
        "--outdir", str(output_dir),
        str(input_path),
    ]

    # headless stability: svp VCL plugin + writable HOME inside the profile
    env = {
        **os.environ,
        "HOME": str(profile_dir),
        "SAL_USE_VCLPLUGIN": "svp",
    }

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        logger.warning("LibreOffice timeout on %s -> %s", input_path.name, target_format)
        return False
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)

    if result.returncode == 0 and expected_output.exists():
        return True

    logger.warning(
        "LibreOffice failed on %s -> %s (code %s): %s",
        input_path.name, target_format, result.returncode,
        (result.stderr or result.stdout or "").strip()[:500],
    )
    return False


def convert_with_libreoffice(input_path: Path, target_format: str, export_filter: str = None) -> Path:
    output_dir = input_path.parent
    expected_output = output_dir / f"{input_path.stem}.{target_format}"

    file_size_mb = input_path.stat().st_size / (1024 * 1024)
    dynamic_timeout = max(120, int(file_size_mb * 15))  # ~15 sec/MB, minimum 120s

    for _ in range(MAX_ATTEMPTS):
        if _attempt(input_path, target_format, export_filter, output_dir, dynamic_timeout):
            return expected_output

    # rescue path: direct Office->PDF layout crashes on some documents, but
    # converting to ODF first then to PDF succeeds
    rescue_format = RESCUE_FORMATS.get(input_path.suffix.lower())
    if target_format == "pdf" and rescue_format:
        intermediate = output_dir / f"{input_path.stem}.{rescue_format}"
        logger.info("Attempting two-stage rescue %s -> %s -> pdf", input_path.name, rescue_format)
        try:
            if _attempt(input_path, rescue_format, None, output_dir, dynamic_timeout) \
                    and _attempt(intermediate, "pdf", None, output_dir, dynamic_timeout) \
                    and expected_output.exists():
                logger.info("Two-stage rescue succeeded for %s", input_path.name)
                return expected_output
        finally:
            intermediate.unlink(missing_ok=True)

    # full details stay in server logs; users get a clean message
    raise HTTPException(
        status_code=500,
        detail=(
            "Conversion failed. The document may use features LibreOffice can't handle — "
            "try re-saving it in its source app and uploading again."
        ),
    )


async def convert_with_libreoffice_async(input_path: Path, target_format: str, export_filter: str = None) -> Path:
    """Runs the blocking LibreOffice call in a threadpool, capped by the
    conversion semaphore so concurrent requests can't OOM the server."""
    async with conversion_semaphore:
        return await asyncio.to_thread(
            convert_with_libreoffice, input_path, target_format, export_filter
        )
