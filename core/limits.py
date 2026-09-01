import asyncio

from core.config import MAX_CONCURRENT_CONVERSIONS

# Caps how many heavy conversions (LibreOffice, Ghostscript, pdf2docx...) run
# at once. Each can eat hundreds of MB of RAM, so unbounded concurrency
# OOM-kills the container under load. Callers must await inside this.
conversion_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CONVERSIONS)
