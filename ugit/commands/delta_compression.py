"""
Delta compression implementation for ugit.

Stores objects as deltas (diffs) instead of full content to save space.
"""

import difflib
import zlib
from typing import Optional, Tuple

from ..core.exceptions import UgitError
from ..core.objects import get_object, hash_object
from ..core.repository import Repository


def create_delta(
    base_sha: str, target_sha: str, repo: Optional[Repository] = None
) -> bytes:
    """
    Create a delta (diff) between two objects.

    Args:
        base_sha: SHA of base object
        target_sha: SHA of target object
        repo: Repository instance

    Returns:
        Delta data as bytes
    """
    if repo is None:
        repo = Repository()

    try:
        # Get both objects
        base_type, base_data = get_object(base_sha, repo=repo)
        target_type, target_data = get_object(target_sha, repo=repo)

        if base_type != target_type:
            raise UgitError("Cannot create delta between different object types")

        # Create delta using difflib
        base_lines = base_data.decode("utf-8", errors="replace").splitlines(
            keepends=True
        )
        target_lines = target_data.decode("utf-8", errors="replace").splitlines(
            keepends=True
        )

        delta = list(
            difflib.unified_diff(
                base_lines,
                target_lines,
                fromfile=base_sha[:7],
                tofile=target_sha[:7],
                lineterm="",
            )
        )

        delta_bytes = "\n".join(delta).encode("utf-8")
        return zlib.compress(delta_bytes)
    except (FileNotFoundError, ValueError) as e:
        raise UgitError(f"Cannot create delta: {e}")


def apply_delta(
    base_sha: str, delta: bytes, repo: Optional[Repository] = None
) -> bytes:
    """
    Apply a delta to a base object to reconstruct the target.

    Args:
        base_sha: SHA of base object
        delta: Compressed delta data
        repo: Repository instance

    Returns:
        Reconstructed object data
    """
    if repo is None:
        repo = Repository()

    try:
        # Decompress delta
        delta_text = zlib.decompress(delta).decode("utf-8")
        delta_lines = delta_text.splitlines()

        # Get base object
        base_type, base_data = get_object(base_sha, repo=repo)
        base_lines = base_data.decode("utf-8", errors="replace").splitlines(
            keepends=True
        )

        # Apply delta (simplified - in production would use proper patch algorithm)
        result_lines = []
        i = 0
        for line in delta_lines:
            if line.startswith("@@"):
                # Parse hunk header
                continue
            elif line.startswith(" "):
                # Context line
                if i < len(base_lines):
                    result_lines.append(base_lines[i])
                    i += 1
            elif line.startswith("+"):
                # Added line
                result_lines.append(line[1:] + "\n")
            elif line.startswith("-"):
                # Removed line
                i += 1

        # Add remaining base lines
        while i < len(base_lines):
            result_lines.append(base_lines[i])
            i += 1

        return "".join(result_lines).encode("utf-8")
    except (FileNotFoundError, ValueError, zlib.error) as e:
        raise UgitError(f"Cannot apply delta: {e}")


def store_delta(
    base_sha: str, target_sha: str, repo: Optional[Repository] = None
) -> Tuple[str, bytes]:
    """
    Store an object as a delta.

    Args:
        base_sha: SHA of base object
        target_sha: SHA of target object
        repo: Repository instance

    Returns:
        Tuple of (delta_sha, delta_data)
    """
    delta_data = create_delta(base_sha, target_sha, repo=repo)
    delta_sha = hash_object(delta_data, "delta", repo=repo)
    return delta_sha, delta_data
