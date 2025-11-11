"""
Bisect command implementation for ugit.

Binary search for finding the commit that introduced a bug.
"""

import os
from typing import Optional

from ..core.exceptions import UgitError
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data, get_current_branch_name
from ..utils.validation import validate_sha


def bisect(
    command: Optional[str] = None,
    bad: Optional[str] = None,
    good: Optional[str] = None,
    reset: bool = False,
) -> None:
    """
    Binary search for finding the commit that introduced a bug.

    Args:
        command: Bisect command (start, good, bad, skip, reset)
        bad: Mark commit as bad
        good: Mark commit as good
        reset: Reset bisect session
    """
    repo = ensure_repository()

    if reset:
        _reset_bisect(repo)
        print("Bisect reset")
        return

    if command == "start":
        if bad and good:
            _start_bisect(repo, bad, good)
        else:
            _start_bisect(repo)
    elif command == "good" or good:
        _mark_commit(repo, good or "HEAD", "good")
    elif command == "bad" or bad:
        _mark_commit(repo, bad or "HEAD", "bad")
    elif command == "skip":
        _skip_commit(repo)
    else:
        _show_status(repo)


def _start_bisect(
    repo: Repository, bad: Optional[str] = None, good: Optional[str] = None
) -> None:
    """Start a bisect session."""
    bisect_dir = os.path.join(repo.ugit_dir, "BISECT")
    os.makedirs(bisect_dir, exist_ok=True)

    if bad:
        if not validate_sha(bad):
            bad_sha = repo.get_head_ref()
            if not bad_sha:
                raise UgitError("No commits in repository")
        else:
            bad_sha = bad
        _mark_commit(repo, bad_sha, "bad")

    if good:
        if not validate_sha(good):
            # Find first commit
            current = repo.get_head_ref()
            while current:
                try:
                    commit_data = get_commit_data(current, repo=repo)
                    parent = commit_data.get("parent")
                    if not parent:
                        break
                    current = parent
                except ValueError:
                    break
            good_sha = current
            if not good_sha:
                raise UgitError("No commits in repository")
        else:
            good_sha = good
        _mark_commit(repo, good_sha, "good")

    _next_commit(repo)


def _mark_commit(repo: Repository, commit: str, status: str) -> None:
    """Mark a commit as good or bad."""
    if not validate_sha(commit):
        head_ref = repo.get_head_ref()
        if not head_ref:
            raise UgitError("No commits in repository")
        commit = head_ref

    bisect_dir = os.path.join(repo.ugit_dir, "BISECT")
    os.makedirs(bisect_dir, exist_ok=True)

    status_file = os.path.join(bisect_dir, status)
    with open(status_file, "a") as f:
        f.write(f"{commit}\n")

    _next_commit(repo)


def _skip_commit(repo: Repository) -> None:
    """Skip current commit."""
    current = repo.get_head_ref()
    if current:
        bisect_dir = os.path.join(repo.ugit_dir, "BISECT")
        skip_file = os.path.join(bisect_dir, "skip")
        with open(skip_file, "a") as f:
            f.write(f"{current}\n")

    _next_commit(repo)


def _next_commit(repo: Repository) -> None:
    """Find and checkout next commit to test."""
    bisect_dir = os.path.join(repo.ugit_dir, "BISECT")

    # Read good and bad commits
    good_commits = set()
    bad_commits = set()
    skipped = set()

    good_file = os.path.join(bisect_dir, "good")
    if os.path.exists(good_file):
        with open(good_file, "r") as f:
            good_commits = set(line.strip() for line in f if line.strip())

    bad_file = os.path.join(bisect_dir, "bad")
    if os.path.exists(bad_file):
        with open(bad_file, "r") as f:
            bad_commits = set(line.strip() for line in f if line.strip())

    skip_file = os.path.join(bisect_dir, "skip")
    if os.path.exists(skip_file):
        with open(skip_file, "r") as f:
            skipped = set(line.strip() for line in f if line.strip())

    if not good_commits or not bad_commits:
        print("Need at least one good and one bad commit")
        return

    # Find midpoint between good and bad
    # Simplified: find a commit between them
    current_bad = list(bad_commits)[0]
    current_good = list(good_commits)[0]

    # Walk from bad to good to find midpoint
    midpoint = _find_midpoint(repo, current_bad, current_good, skipped)

    if midpoint:
        from ..core.checkout import checkout_commit

        checkout_commit(repo, midpoint)
        print(f"Bisecting: commit {midpoint[:7]}")
        print("Mark this commit as (g)ood or (b)ad")
    else:
        print("No more commits to test")
        _show_result(repo, current_bad)


def _find_midpoint(
    repo: Repository, bad_sha: str, good_sha: str, skipped: set
) -> Optional[str]:
    """Find midpoint commit between good and bad."""
    # Get all commits between bad and good
    commits = []
    current = bad_sha
    visited = set()

    while current and current not in visited:
        visited.add(current)
        if current == good_sha:
            break
        commits.append(current)
        try:
            commit_data = get_commit_data(current, repo=repo)
            parent = commit_data.get("parent")
            if parent is not None:
                current = parent
            else:
                break
        except ValueError:
            break

    # Filter out skipped commits
    commits = [c for c in commits if c not in skipped]

    if len(commits) <= 1:
        return None

    # Return midpoint
    return commits[len(commits) // 2]


def _show_result(repo: Repository, bad_sha: str) -> None:
    """Show bisect result."""
    try:
        commit_data = get_commit_data(bad_sha, repo=repo)
        print(f"\nFirst bad commit: {bad_sha}")
        print(f"Author: {commit_data.get('author', 'Unknown')}")
        print(f"Message: {commit_data.get('message', 'No message')}")
    except ValueError:
        print(f"First bad commit: {bad_sha}")


def _show_status(repo: Repository) -> None:
    """Show current bisect status."""
    bisect_dir = os.path.join(repo.ugit_dir, "BISECT")
    if not os.path.exists(bisect_dir):
        print("No bisect session in progress")
        return

    good_file = os.path.join(bisect_dir, "good")
    bad_file = os.path.join(bisect_dir, "bad")

    good_count = 0
    bad_count = 0

    if os.path.exists(good_file):
        with open(good_file, "r") as f:
            good_count = len([l for l in f if l.strip()])

    if os.path.exists(bad_file):
        with open(bad_file, "r") as f:
            bad_count = len([l for l in f if l.strip()])

    print(f"Bisect status: {good_count} good, {bad_count} bad")


def _reset_bisect(repo: Repository) -> None:
    """Reset bisect session."""
    bisect_dir = os.path.join(repo.ugit_dir, "BISECT")
    if os.path.exists(bisect_dir):
        import shutil

        shutil.rmtree(bisect_dir)
