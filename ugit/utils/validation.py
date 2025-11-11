"""
Input validation utilities for ugit.

Provides validation functions for paths, SHAs, and other inputs
to prevent security issues and data corruption.
"""

import os
from typing import Optional


def validate_sha(sha: str) -> bool:
    """
    Validate that a string is a valid SHA-1 hash.

    Args:
        sha: String to validate

    Returns:
        True if valid SHA-1 hash (40 hex characters)
    """
    if len(sha) != 40:
        return False
    try:
        int(sha, 16)  # Check if it's valid hex
    except ValueError:
        return False
    return True


def validate_path(path: str, base_path: Optional[str] = None) -> bool:
    """
    Validate that a path is safe and doesn't contain traversal attempts.

    Args:
        path: Path to validate
        base_path: Base directory to resolve against (prevents escaping)

    Returns:
        True if path is safe
    """
    if not path:
        return False

    # Normalize the path
    try:
        normalized = os.path.normpath(path)
    except (ValueError, OSError):
        return False

    # Check for path traversal attempts
    if ".." in normalized.split(os.sep):
        return False

    # If base_path is provided, ensure path is within it
    if base_path:
        try:
            base = os.path.abspath(base_path)
            full_path = os.path.abspath(os.path.join(base, normalized))
            if not full_path.startswith(base):
                return False
        except (OSError, ValueError):
            return False

    return True


def sanitize_path(path: str) -> str:
    """
    Sanitize a file path by normalizing it.

    Args:
        path: Path to sanitize

    Returns:
        Normalized path

    Raises:
        ValueError: If path is invalid
    """
    try:
        normalized = os.path.normpath(path)
        # Replace backslashes with forward slashes for consistency
        normalized = normalized.replace(os.sep, "/")
        return normalized
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid path: {path}") from e


def validate_branch_name(name: str) -> bool:
    """
    Validate a branch name according to Git conventions.

    Args:
        name: Branch name to validate

    Returns:
        True if valid branch name
    """
    if not name or not isinstance(name, str):
        return False

    # Git branch name rules:
    # - Cannot be empty
    # - Cannot start with . or end with .lock
    # - Cannot contain consecutive dots
    # - Cannot contain certain special characters
    if name.startswith(".") or name.endswith(".lock"):
        return False

    if ".." in name:
        return False

    # Check for invalid characters
    invalid_chars = ["~", "^", ":", "?", "*", "[", " ", "\\"]
    for char in invalid_chars:
        if char in name:
            return False

    # Check for control characters
    if any(ord(c) < 32 for c in name):
        return False

    return True
