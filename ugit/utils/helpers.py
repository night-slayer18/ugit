"""Utility functions for ugit."""

import os
import time
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional

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


def walk_files(
    directory: str = ".", ignore_patterns: Optional[list] = None
) -> Iterator[str]:
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


def get_ignored_patterns(repo_path: str = ".") -> list:
    """
    Get ignore patterns from .ugitignore file.
    
    Args:
        repo_path: Path to repository root
    
    Returns:
        List of ignore patterns
    """
    patterns = [".ugit"]  # Always ignore .ugit directory
    ignore_file = os.path.join(repo_path, ".ugitignore")
    
    if os.path.exists(ignore_file):
        try:
            with open(ignore_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except (IOError, OSError):
            pass
    
    return patterns


def get_commit_data(commit_sha: str) -> Dict[str, Any]:
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
        result = json.loads(data.decode())
        if not isinstance(result, dict):
            raise ValueError(f"Invalid commit data format")
        return result
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Invalid commit {commit_sha}: {e}")
