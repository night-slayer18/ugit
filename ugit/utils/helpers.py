"""Utility functions for ugit."""

import os
import time
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from ..core.repository import Repository


def find_repository_root(path: str = ".") -> str:
    """
    Find the root of the ugit repository.

    Args:
        path: Starting path to search from

    Returns:
        Path to repository root

    Raises:
        RuntimeError: If not in a repository
    """
    current = os.path.abspath(path)

    while current != os.path.dirname(current):  # Not at filesystem root
        if os.path.exists(os.path.join(current, ".ugit")):
            return current
        current = os.path.dirname(current)

    raise RuntimeError("Not in a ugit repository")


def format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp for display."""
    try:
        from datetime import datetime

        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%a %b %d %H:%M:%S %Y %z")
    except (ValueError, AttributeError):
        return timestamp


def walk_files(directory: str = ".", ignore_patterns: list = None) -> Iterator[str]:
    """
    Walk files in directory, respecting ignore patterns.

    Args:
        directory: Directory to walk
        ignore_patterns: Patterns to ignore (defaults to ['.ugit'])

    Yields:
        Relative file paths
    """
    if ignore_patterns is None:
        ignore_patterns = [".ugit"]

    for root, dirs, files in os.walk(directory):
        # Remove ignored directories
        dirs[:] = [
            d
            for d in dirs
            if not any(d.startswith(pattern) for pattern in ignore_patterns)
        ]

        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), directory)
            if not any(file_path.startswith(pattern) for pattern in ignore_patterns):
                yield file_path.replace(os.sep, "/")  # Normalize separators


def safe_read_file(path: str) -> bytes:
    """
    Safely read file contents.

    Args:
        path: File path to read

    Returns:
        File contents as bytes

    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If file cannot be read
    """
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except (IOError, OSError) as e:
        raise RuntimeError(f"Cannot read file {path}: {e}")


def ensure_repository() -> "Repository":
    """
    Ensure we're in a repository and return Repository instance.

    Returns:
        Repository instance

    Raises:
        SystemExit: If not in a repository
    """
    from ..core.repository import Repository

    repo = Repository()
    if not repo.is_repository():
        print("Not a ugit repository")
        raise SystemExit(1)
    return repo


def get_commit_data(commit_sha: str) -> dict:
    """
    Get commit data from SHA.

    Args:
        commit_sha: SHA of the commit

    Returns:
        Parsed commit data

    Raises:
        ValueError: If not a valid commit
    """
    import json

    from ..core.objects import get_object

    try:
        type_, data = get_object(commit_sha)
        if type_ != "commit":
            raise ValueError(f"Expected commit object, got {type_}")
        return json.loads(data.decode())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Invalid commit {commit_sha}: {e}")
