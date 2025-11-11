"""
Atomic file operations for ugit.

Provides atomic write operations to prevent corruption during
critical file updates (index, refs, config).
"""

import os
import tempfile
from pathlib import Path
from typing import Union


def atomic_write(
    file_path: str,
    content: Union[bytes, str],
    mode: str = "wb",
    create_dirs: bool = True,
) -> None:
    """
    Atomically write content to a file.

    Uses a temporary file and rename to ensure atomicity.
    This prevents corruption if the process is interrupted.

    Args:
        file_path: Path to the file to write
        content: Content to write (bytes or str)
        mode: File mode ('wb' for bytes, 'w' for text)
        create_dirs: Whether to create parent directories if needed

    Raises:
        OSError: If the write operation fails
    """
    path = Path(file_path)
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    # Convert content to bytes if needed
    content_bytes: bytes
    if isinstance(content, str):
        if mode == "wb":
            content_bytes = content.encode("utf-8")
        else:
            content_bytes = content.encode("utf-8")
            mode = "wb"
    else:
        content_bytes = content
        if mode == "w":
            mode = "wb"

    # Write to temporary file in same directory
    temp_dir = path.parent
    temp_fd, temp_path = tempfile.mkstemp(
        dir=str(temp_dir), prefix=f".{path.name}.tmp.", suffix=""
    )

    try:
        with os.fdopen(temp_fd, mode) as f:
            f.write(content_bytes)
            f.flush()
            os.fsync(f.fileno())  # Ensure data is written to disk

        # Atomic rename
        os.replace(temp_path, file_path)
    except Exception:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def atomic_write_text(
    file_path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True
) -> None:
    """
    Atomically write text content to a file.

    Args:
        file_path: Path to the file to write
        content: Text content to write
        encoding: Text encoding (default: utf-8)
        create_dirs: Whether to create parent directories if needed

    Raises:
        OSError: If the write operation fails
    """
    atomic_write(
        file_path, content.encode(encoding), mode="wb", create_dirs=create_dirs
    )
