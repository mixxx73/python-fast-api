"""Application-wide constants resolved from environment variables."""

import os
from uuid import UUID

# Hardcoded defaults; can be overridden via env vars
_DEFAULT_ID = UUID("11111111-1111-1111-1111-111111111111")


def _read_uuid(var: str, fallback: UUID) -> UUID:
    """Read a UUID from an environment variable, falling back to a default."""
    val = os.getenv(var)
    if val:
        try:
            return UUID(val)
        except Exception:
            # Invalid format, ignore and use fallback
            pass
    return fallback


DEFAULT_GROUP_ID: UUID = _read_uuid("DEFAULT_GROUP_ID", _DEFAULT_ID)
DEFAULT_GROUP_NAME: str = os.getenv("DEFAULT_GROUP_NAME", "default")
