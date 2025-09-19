"""
Show repository status.
"""

import json
import os
from typing import List, Set

from ..core.objects import get_object, hash_object
from ..core.repository import Index, Repository
from ..utils.helpers import ensure_repository, walk_files


def status() -> None:
    """Display the status of the working directory and staging area."""
    repo = ensure_repository()

    index = Index(repo)
    index_data = index.read()

    # Get current HEAD commit for comparison
    head_sha = repo.get_head_ref()
    committed_files = _get_committed_files(head_sha) if head_sha else {}

    # Categorize files
    staged_files = _get_staged_files(index_data, committed_files)
    modified_files = _get_modified_files(index_data)
    untracked_files = _get_untracked_files(set(index_data.keys()))
    deleted_files = _get_deleted_files(set(index_data.keys()))

    # Display status sections
    if staged_files:
        _print_status_section("Changes to be committed:", staged_files, "green")

    if modified_files:
        _print_status_section("Changes not staged for commit:", modified_files, "red")

    if deleted_files:
        _print_status_section("Deleted files:", deleted_files, "red")

    if untracked_files:
        _print_status_section("Untracked files:", untracked_files, "red")

    if not any([staged_files, modified_files, untracked_files, deleted_files]):
        print("Nothing to commit, working tree clean")


def _get_committed_files(head_sha: str) -> dict:
    """Get files from the current HEAD commit."""
    try:
        type_, data = get_object(head_sha)
        if type_ != "commit":
            return {}

        commit = json.loads(data.decode())
        tree_sha = commit["tree"]

        type_, tree_data = get_object(tree_sha)
        if type_ != "tree":
            return {}

        tree = json.loads(tree_data.decode())
        return dict(tree)
    except Exception:
        return {}


def _get_staged_files(index_data: dict, committed_files: dict) -> List[str]:
    """Get list of files staged for commit."""
    staged = []
    for path, sha in index_data.items():
        if path not in committed_files or committed_files[path] != sha:
            status_char = "A" if path not in committed_files else "M"
            staged.append(f"{status_char} {path}")
    return staged


def _get_modified_files(index_data: dict) -> List[str]:
    """Get list of tracked files that have been modified."""
    modified = []
    for path, stored_sha in index_data.items():
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    data = f.read()
                current_sha = hash_object(data, "blob", write=False)
                if current_sha != stored_sha:
                    modified.append(f"M {path}")
            except (IOError, OSError):
                modified.append(f"M {path}")
    return modified


def _get_untracked_files(tracked_files: Set[str]) -> List[str]:
    """Get list of untracked files."""
    untracked = []
    for file_path in walk_files():
        if file_path not in tracked_files:
            untracked.append(f"? {file_path}")
    return untracked


def _get_deleted_files(tracked_files: Set[str]) -> List[str]:
    """Get list of tracked files that have been deleted."""
    deleted = []
    for path in tracked_files:
        if not os.path.exists(path):
            deleted.append(f"D {path}")
    return deleted


def _print_status_section(title: str, files: List[str], color: str) -> None:
    """Print a section of the status output."""
    if files:
        print(f"\n{title}")
        for file in sorted(files):  # Sort for consistent output
            print(f"  {file}")
