"""
Reset command implementation for ugit.

This module handles resetting the staging area and working directory.
"""

import os
from typing import List, Optional

from ..core.objects import get_object
from ..core.repository import Repository
from ..utils.helpers import ensure_repository


def reset(target: Optional[str] = None, hard: bool = False, soft: bool = False) -> None:
    """
    Reset current HEAD to the specified state.

    Args:
        target: Commit SHA or branch to reset to (default: HEAD)
        hard: Reset working directory and staging area
        soft: Only move HEAD, keep staging and working directory
    """
    repo = ensure_repository()

    if soft and hard:
        print("Cannot specify both --soft and --hard")
        return

    if target:
        # Reset to specific commit
        _reset_to_commit(repo, target, hard, soft)
    else:
        # Reset staging area (default behavior)
        _reset_staging_area(repo)


def unstage(file_paths: Optional[List[str]] = None) -> None:
    """
    Remove files from staging area without affecting working directory.

    Args:
        file_paths: List of files to unstage (None = all files)
    """
    repo = ensure_repository()

    if file_paths:
        for file_path in file_paths:
            _unstage_file(repo, file_path)
    else:
        _reset_staging_area(repo)


def _reset_to_commit(
    repo: Repository, target: str, hard: bool = False, soft: bool = False
) -> None:
    """Reset HEAD to a specific commit."""
    try:
        # Resolve target (could be commit SHA or branch name)
        commit_sha = _resolve_target(repo, target)

        if not commit_sha:
            print(f"Error: Cannot resolve '{target}'")
            return

        # Validate commit exists
        try:
            commit_type, commit_data = get_object(commit_sha)
            if commit_type != "commit":
                print(f"Error: {target} is not a commit")
                return
        except FileNotFoundError:
            print(f"Error: Commit {target} not found")
            return

        # Update HEAD
        head_path = os.path.join(repo.ugit_dir, "HEAD")
        with open(head_path, "w", encoding="utf-8") as f:
            f.write(commit_sha)

        if hard:
            # Reset working directory and staging area
            _reset_working_directory(repo, commit_sha)
            _clear_staging_area(repo)
            print(f"Hard reset to {commit_sha[:7]}")
        elif soft:
            # Only move HEAD
            print(f"Soft reset to {commit_sha[:7]}")
        else:
            # Mixed reset (default) - reset staging area but keep working directory
            _clear_staging_area(repo)
            print(f"Reset to {commit_sha[:7]}")

    except Exception as e:
        print(f"Error during reset: {e}")


def _reset_staging_area(repo: Repository) -> None:
    """Reset the staging area (clear index)."""
    index_path = os.path.join(repo.ugit_dir, "index")

    if os.path.exists(index_path):
        os.remove(index_path)
        print("Unstaged all files")
    else:
        print("Nothing to unstage")


def _clear_staging_area(repo: Repository) -> None:
    """Clear the staging area without output."""
    index_path = os.path.join(repo.ugit_dir, "index")
    if os.path.exists(index_path):
        os.remove(index_path)


def _reset_working_directory(repo: Repository, commit_sha: str) -> None:
    """Reset working directory to match a commit."""
    try:
        # Use checkout functionality to restore files
        from .checkout import _checkout_commit

        _checkout_commit(repo, commit_sha)
    except Exception as e:
        print(f"Error resetting working directory: {e}")


def _unstage_file(repo: Repository, file_path: str) -> None:
    """Remove a specific file from the staging area."""
    index_path = os.path.join(repo.ugit_dir, "index")

    if not os.path.exists(index_path):
        print(f"'{file_path}' is not staged")
        return

    # Read current index
    staged_files = []
    file_found = False

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 1)  # Split on space, not tab
            if len(parts) >= 2:
                staged_file_path = parts[1]
                if staged_file_path == file_path:
                    file_found = True
                    continue
                staged_files.append(line)

    if not file_found:
        print(f"'{file_path}' is not staged")
        return

    # Write back the index without the unstaged file
    if staged_files:
        with open(index_path, "w", encoding="utf-8") as f:
            for line in staged_files:
                f.write(line + "\n")
    else:
        # No files left in index
        os.remove(index_path)

    print(f"Unstaged '{file_path}'")


def _resolve_target(repo: Repository, target: str) -> Optional[str]:
    """Resolve a target (commit SHA or branch name) to commit SHA."""
    # Check if it's a branch name
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", target)
    if os.path.exists(branch_path):
        with open(branch_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # Check if it's HEAD
    if target.upper() == "HEAD":
        return repo.get_head_ref()

    # Assume it's a commit SHA
    if len(target) >= 4:  # Allow short SHAs
        # Try to find full SHA that starts with the given prefix
        objects_dir = os.path.join(repo.ugit_dir, "objects")
        if os.path.exists(objects_dir):
            for subdir in os.listdir(objects_dir):
                if len(subdir) == 2:
                    subdir_path = os.path.join(objects_dir, subdir)
                    if os.path.isdir(subdir_path):
                        for obj_file in os.listdir(subdir_path):
                            full_sha = subdir + obj_file
                            if full_sha.startswith(target):
                                return full_sha

    return target if len(target) == 40 else None
