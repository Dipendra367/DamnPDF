MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

RETENTION_HOURS = 1          # user files auto-deleted after this long
SWEEP_INTERVAL_MINUTES = 15  # how often the cleanup task runs

MAX_CONCURRENT_CONVERSIONS = 3  # heavy conversion jobs running at once

RATE_LIMIT_PER_MINUTE = 30  # requests per client IP per minute