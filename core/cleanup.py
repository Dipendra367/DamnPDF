import asyncio
import logging
import shutil
import time
from pathlib import Path

from core.config import RETENTION_HOURS, SWEEP_INTERVAL_MINUTES

logger = logging.getLogger("damnpdf.cleanup")

TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)


def sweep_temp_dir():
    """Delete every file and directory in TEMP_DIR older than RETENTION_HOURS."""
    cutoff = time.time() - RETENTION_HOURS * 3600
    for entry in TEMP_DIR.iterdir():
        try:
            if entry.stat().st_mtime < cutoff:
                if entry.is_dir():
                    shutil.rmtree(entry, ignore_errors=True)
                else:
                    entry.unlink(missing_ok=True)
        except OSError:
            continue


async def sweeper_loop():
    """Background task: sweep the temp dir on startup, then at a fixed interval."""
    while True:
        try:
            sweep_temp_dir()
        except Exception:
            logger.exception("Temp dir sweep failed")
        await asyncio.sleep(SWEEP_INTERVAL_MINUTES * 60)
