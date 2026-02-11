"""Application-wide constants and security defaults."""

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Rate limit defaults (can be overridden by environment variables).
DEFAULT_RATE_LIMIT = "60/minute"
AUTHENTICATED_RATE_LIMIT = "120/minute"
