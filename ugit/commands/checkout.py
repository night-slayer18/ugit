"""
Checkout files from a specific commit.
"""

import json
import os
import shutil
from typing import Dict, List, Tuple

from ..core.objects import get_object
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data


def checkout(commit_sha: str) -> None:
    """
    Checkout files from a specific commit.

    Args:
        commit_sha: SHA hash of the commit to checkout
    """
    repo = ensure_repository()

    try:
        # Get commit data using helper function
        commit = get_commit_data(commit_sha)
        tree_sha = commit["tree"]

        # Get tree object
        type_, tree_data = get_object(tree_sha)
        if type_ != "tree":
            print(f"Error: Invalid tree object in commit")
            return

        tree = json.loads(tree_data.decode())

        # Clear existing files (except .ugit and main files)
        _clear_working_directory(repo)

        # Write files from the tree
        for path, sha in tree:
            _restore_file(path, sha)

        print(f"Checked out commit {commit_sha[:7]}")

    except ValueError as e:
        print(f"Error checking out commit {commit_sha}: {e}")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error checking out commit {commit_sha}: {e}")


def _clear_working_directory() -> None:
    """Clear working directory of tracked files."""
    for root, dirs, files in os.walk(".", topdown=False):
        # Skip .ugit directory
        if ".ugit" in dirs:
            dirs.remove(".ugit")

        for file in files:
            path = os.path.relpath(os.path.join(root, file))
            # Keep ugit-related files
            if not (path.startswith(".ugit") or path.endswith("ugit.py")):
                try:
                    os.remove(path)
                except OSError:
                    pass  # File might be read-only or in use

        # Remove empty directories
        for dir in dirs:
            dir_path = os.path.relpath(os.path.join(root, dir))
            if not dir_path.startswith(".ugit"):
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except OSError:
                    pass


def _restore_file(path: str, sha: str) -> None:
    """Restore a single file from object storage."""
    try:
        # Create directory if needed
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        # Get file content and write to disk
        type_, content = get_object(sha)
        if type_ != "blob":
            print(f"Warning: Expected blob for {path}, got {type_}")
            return

        with open(path, "wb") as f:
            f.write(content)

    except (FileNotFoundError, OSError) as e:
        print(f"Error restoring {path}: {e}")
