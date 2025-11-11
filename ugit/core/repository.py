"""
Repository management for ugit.

This module handles repository initialization, index management,
and repository state operations.
"""

import os
import sys
from typing import Dict, Optional, Tuple

from ..utils.atomic import atomic_write_text
from ..utils.cache import get_repo_cache


class Repository:
    """Represents a ugit repository."""

    def __init__(self, path: str = "."):
        """
        Initialize repository object.

        Args:
            path: Path to repository root
        """
        self.path = os.path.abspath(path)
        self.ugit_dir = os.path.join(self.path, ".ugit")

    def is_repository(self) -> bool:
        """Check if current directory is a ugit repository."""
        return os.path.exists(self.ugit_dir) and os.path.isdir(self.ugit_dir)

    def get_head_ref(self) -> Optional[str]:
        """Get the current HEAD reference."""
        head_path = os.path.join(self.ugit_dir, "HEAD")
        if not os.path.exists(head_path):
            return None

        try:
            with open(head_path, "r", encoding="utf-8") as f:
                head_content = f.read().strip()

            if head_content.startswith("ref: "):
                ref_path = head_content[5:]  # Remove "ref: " prefix
                ref_file = os.path.join(self.ugit_dir, ref_path)
                if os.path.exists(ref_file):
                    with open(ref_file, "r", encoding="utf-8") as f:
                        return f.read().strip()
                else:
                    # This case happens on the first commit of a new repository
                    return None

            # Detached HEAD
            return head_content if head_content else None
        except (IOError, OSError, UnicodeDecodeError) as e:
            print(f"Error reading HEAD: {e}", file=sys.stderr)
            return None

    def set_head_ref(self, sha: str, branch: str = "main") -> None:
        """
        Set the HEAD reference to a commit SHA.

        Args:
            sha: Commit SHA to set
            branch: Branch name (default: "main")

        Raises:
            RuntimeError: If setting the reference fails
        """
        branch_dir = os.path.join(self.ugit_dir, "refs", "heads")
        os.makedirs(branch_dir, exist_ok=True)

        branch_path = os.path.join(branch_dir, branch)
        try:
            atomic_write_text(branch_path, sha, create_dirs=True)
        except (IOError, OSError) as e:
            raise RuntimeError(f"Failed to set HEAD reference: {e}")


class Index:
    """Manages the staging area (index) for a repository."""

    def __init__(self, repo: Repository):
        """
        Initialize index for a repository.

        Args:
            repo: Repository instance
        """
        self.repo = repo
        self.index_path = os.path.join(repo.ugit_dir, "index")
        self._cache = get_repo_cache()
        self._cache_key = f"index:{self.index_path}"

    def read(self) -> Dict[str, Tuple[str, float, int]]:
        """
        Read the current index (with caching).

        Returns:
            Dictionary mapping file paths to (SHA, mtime, size) tuples.
        """
        # Check cache first
        cached = self._cache.get(self._cache_key)
        if cached is not None:
            # Type assertion: cache returns the same type we store
            return cached  # type: ignore[no-any-return]

        index = {}
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue

                        # New format: sha mtime size path
                        parts = line.split(" ", 3)
                        if len(parts) != 4:
                            print(
                                f"Invalid index line {line_num}: {line}",
                                file=sys.stderr,
                            )
                            continue

                        sha, mtime_str, size_str, path = parts
                        if len(sha) != 40:
                            print(
                                f"Invalid SHA in index line {line_num}", file=sys.stderr
                            )
                            continue

                        try:
                            index[path] = (sha, float(mtime_str), int(size_str))
                        except (ValueError, TypeError):
                            print(
                                f"Invalid metadata in index line {line_num}",
                                file=sys.stderr,
                            )
                            continue
            except (IOError, OSError, UnicodeDecodeError) as e:
                print(f"Error reading index: {e}", file=sys.stderr)

        # Cache the result
        self._cache.set(self._cache_key, index)
        return index

    def write(self, index: Dict[str, Tuple[str, float, int]]) -> None:
        """
        Write index to disk using atomic write operation.

        Args:
            index: Dictionary mapping file paths to (SHA, mtime, size) tuples.

        Raises:
            RuntimeError: If writing the index fails
        """
        try:
            # Build index content
            lines = []
            for path, (sha, mtime, size) in sorted(index.items()):
                lines.append(f"{sha} {mtime} {size} {path}\n")

            content = "".join(lines)
            atomic_write_text(self.index_path, content, create_dirs=True)

            # Invalidate cache
            self._cache.invalidate(self._cache_key)
        except (IOError, OSError) as e:
            raise RuntimeError(f"Failed to write index: {e}")
