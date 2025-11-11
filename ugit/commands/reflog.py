"""
Reflog command implementation for ugit.

Tracks history of HEAD and branch movements for recovery purposes.
"""

import json
import os
from datetime import datetime
from typing import List, Optional

from ..core.repository import Repository
from ..utils.atomic import atomic_write_text
from ..utils.helpers import ensure_repository, get_current_branch_name


def reflog(show: Optional[str] = None, branch: Optional[str] = None) -> None:
    """
    Show reflog entries.

    Args:
        show: Show specific entry (not implemented yet)
        branch: Show reflog for specific branch (default: current branch or HEAD)
    """
    repo = ensure_repository()
    _show_reflog(repo, branch)


def _show_reflog(repo: Repository, branch: Optional[str] = None) -> None:
    """Display reflog entries."""
    if branch is None:
        branch = get_current_branch_name(repo) or "HEAD"

    reflog_path = _get_reflog_path(repo, branch)
    if not os.path.exists(reflog_path):
        print(f"No reflog entries for {branch}")
        return

    try:
        with open(reflog_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            print(f"No reflog entries for {branch}")
            return

        # Display entries (newest first)
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t", 1)
            if len(parts) == 2:
                sha, message = parts
                print(f"{sha[:7]} {message}")
    except (IOError, OSError) as e:
        print(f"Error reading reflog: {e}")


def append_reflog(
    repo: Repository, branch: str, old_sha: Optional[str], new_sha: str, message: str
) -> None:
    """
    Append an entry to the reflog.

    Args:
        repo: Repository instance
        branch: Branch name (or "HEAD")
        old_sha: Previous commit SHA (None for new branches)
        new_sha: New commit SHA
        message: Reflog message
    """
    reflog_path = _get_reflog_path(repo, branch)
    os.makedirs(os.path.dirname(reflog_path), exist_ok=True)

    # Format: new_sha\tmessage
    entry = f"{new_sha}\t{message}\n"

    # Append to reflog file
    try:
        with open(reflog_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except (IOError, OSError):
        # If append fails, try atomic write
        try:
            existing = ""
            if os.path.exists(reflog_path):
                with open(reflog_path, "r", encoding="utf-8") as f:
                    existing = f.read()
            atomic_write_text(reflog_path, existing + entry, create_dirs=True)
        except (IOError, OSError) as e:
            # Reflog is not critical, just log and continue
            pass


def _get_reflog_path(repo: Repository, branch: str) -> str:
    """
    Get the reflog file path for a branch.

    Args:
        repo: Repository instance
        branch: Branch name

    Returns:
        Path to reflog file
    """
    if branch == "HEAD":
        return os.path.join(repo.ugit_dir, "logs", "HEAD")
    else:
        return os.path.join(repo.ugit_dir, "logs", "refs", "heads", branch)


def get_reflog_entries(
    repo: Repository, branch: str, limit: Optional[int] = None
) -> List[dict]:
    """
    Get reflog entries for a branch.

    Args:
        repo: Repository instance
        branch: Branch name
        limit: Maximum number of entries to return

    Returns:
        List of reflog entries as dicts with 'sha' and 'message' keys
    """
    reflog_path = _get_reflog_path(repo, branch)
    if not os.path.exists(reflog_path):
        return []

    entries = []
    try:
        with open(reflog_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split("\t", 1)
                if len(parts) == 2:
                    sha, message = parts
                    entries.append({"sha": sha, "message": message})

                if limit and len(entries) >= limit:
                    break
    except (IOError, OSError):
        pass

    return entries
