"""
Repository management for ugit.

This module handles repository initialization, index management,
and repository state operations.
"""

import os
from typing import Dict, Optional


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

            return head_content if head_content else None
        except (IOError, OSError, UnicodeDecodeError) as e:
            print(f"Error reading HEAD: {e}")
            return None

    def set_head_ref(self, sha: str, branch: str = "main") -> None:
        """Set the HEAD reference to a commit SHA."""
        branch_dir = os.path.join(self.ugit_dir, "refs", "heads")
        os.makedirs(branch_dir, exist_ok=True)

        branch_path = os.path.join(branch_dir, branch)
        try:
            with open(branch_path, "w", encoding="utf-8") as f:
                f.write(sha)
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

    def read(self) -> Dict[str, str]:
        """
        Read the current index.

        Returns:
            Dictionary mapping file paths to SHA hashes
        """
        index = {}
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line:
                            parts = line.split(" ", 1)
                            if len(parts) != 2:
                                print(f"Warning: Invalid index line {line_num}: {line}")
                                continue
                            sha, path = parts
                            if len(sha) != 40:
                                print(f"Warning: Invalid SHA in index line {line_num}")
                                continue
                            index[path] = sha
            except (IOError, OSError, UnicodeDecodeError) as e:
                print(f"Error reading index: {e}")
        return index

    def write(self, index: Dict[str, str]) -> None:
        """
        Write index to disk.

        Args:
            index: Dictionary mapping file paths to SHA hashes
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

            with open(self.index_path, "w", encoding="utf-8") as f:
                for path, sha in sorted(index.items()):  # Sort for consistency
                    f.write(f"{sha} {path}\n")
        except (IOError, OSError) as e:
            raise RuntimeError(f"Failed to write index: {e}")

    def add_file(self, path: str, sha: str) -> None:
        """
        Add a file to the index.

        Args:
            path: File path
            sha: SHA hash of the file content
        """
        if len(sha) != 40:
            raise ValueError(f"Invalid SHA length: {len(sha)}")

        index = self.read()
        # Normalize path separators
        normalized_path = os.path.normpath(path).replace(os.sep, "/")
        index[normalized_path] = sha
        self.write(index)

    def remove_file(self, path: str) -> None:
        """
        Remove a file from the index.

        Args:
            path: File path to remove
        """
        index = self.read()
        normalized_path = os.path.normpath(path).replace(os.sep, "/")
        if normalized_path in index:
            del index[normalized_path]
            self.write(index)
