# Copyright (c) 2026 Xist.GG LLC

import os
import glob
import portalocker
import time
from pathlib import Path

STORAGE_DIR = Path("data")
TRANSIT_DIR = STORAGE_DIR / "transit"

def init_storage():
    """Ensures the storage directory exists."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    TRANSIT_DIR.mkdir(parents=True, exist_ok=True)

def _get_file_path(uuid: str) -> Path:
    return STORAGE_DIR / uuid

def save(uuid: str, data: bytes):
    """Saves encrypted data to a file with locking."""
    filepath = _get_file_path(uuid)
    # Using 'wb' writes bytes.
    # portalocker.LOCK_EX ensures exclusive access.
    with portalocker.Lock(filepath, 'wb', flags=portalocker.LOCK_EX) as f:
        f.write(data)

def load(uuid: str) -> bytes | None:
    """Loads encrypted data from a file."""
    filepath = _get_file_path(uuid)
    if not filepath.exists():
        return None
    
    try:
        # Use shared lock for reading
        with portalocker.Lock(filepath, 'rb', flags=portalocker.LOCK_SH) as f:
            return f.read()
    except (FileNotFoundError, portalocker.LockException):
        return None

def exists(uuid: str) -> bool:
    """Checks if a secret exists."""
    return _get_file_path(uuid).exists()

def delete(uuid: str):
    """Deletes a secret file."""
    filepath = _get_file_path(uuid)
    try:
        if filepath.exists():
            os.remove(filepath)
    except OSError:
        pass # Best effort

def cleanup(max_age_seconds: int = 86400 * 7): # Default 7 days
    """Deletes files older than max_age_seconds."""
    now = time.time()
    for filepath in STORAGE_DIR.glob("*"):
        if filepath.is_file():
            try:
                stat = filepath.stat()
                if now - stat.st_mtime > max_age_seconds:
                    os.remove(filepath)
            except OSError:
                pass
