"""
Interactive staging (add -i) implementation for ugit.

Allows users to selectively stage files with an interactive interface.
"""

import os
import sys
from typing import Dict, List, Set, Tuple

from ..core.exceptions import UgitError
from ..core.repository import Index, Repository
from ..utils.helpers import ensure_repository, get_ignored_patterns, should_ignore_file
from .add import _add_single_path


def add_interactive() -> None:
    """Interactive staging interface."""
    repo = ensure_repository()
    index = Index(repo)
    index_data = index.read()
    ignored_patterns = get_ignored_patterns(repo.path)

    # Get all modified and untracked files
    files = _get_candidate_files(repo, index_data, ignored_patterns)

    if not files:
        print("No files to stage")
        return

    # Show files and get user selection
    staged = _interactive_select(repo, files, index_data)

    if staged:
        # Stage selected files
        for file_path in staged:
            _add_single_path(file_path, index_data, ignored_patterns, [])

        index.write(index_data)
        print(f"\nStaged {len(staged)} file(s)")


def _get_candidate_files(
    repo: Repository,
    index_data: Dict[str, Tuple[str, float, int]],
    ignored_patterns: List[str],
) -> List[Tuple[str, str]]:
    """Get files that can be staged (modified or untracked)."""
    files = []

    # Check working directory
    for root, dirs, filenames in os.walk(repo.path):
        # Skip .ugit directory
        if ".ugit" in root:
            continue

        for filename in filenames:
            file_path = os.path.relpath(os.path.join(root, filename), repo.path)

            if should_ignore_file(file_path, ignored_patterns):
                continue

            # Check if modified or untracked
            status = _get_file_status(repo, file_path, index_data)
            if status in ("modified", "untracked"):
                files.append((file_path, status))

    return sorted(files)


def _get_file_status(
    repo: Repository, file_path: str, index_data: Dict[str, Tuple[str, float, int]]
) -> str:
    """Get status of a file (modified, untracked, or unchanged)."""
    full_path = os.path.join(repo.path, file_path)

    if not os.path.exists(full_path):
        return "deleted"

    if file_path not in index_data:
        return "untracked"

    # Check if modified
    try:
        from ..core.objects import hash_object

        with open(full_path, "rb") as f:
            content = f.read()
        current_sha = hash_object(content, "blob", repo=repo)

        stored_sha, _, _ = index_data[file_path]
        if current_sha != stored_sha:
            return "modified"

        return "unchanged"
    except (IOError, OSError):
        return "error"


def _interactive_select(
    repo: Repository, files: List[Tuple[str, str]], index_data: Dict
) -> Set[str]:
    """Interactive file selection interface."""
    print("\nInteractive staging:")
    print("=" * 60)

    selected: Set[str] = set()
    i = 1

    # Show files with numbers
    for file_path, status in files:
        status_symbol = {"modified": "M", "untracked": "?", "deleted": "D"}.get(
            status, " "
        )
        print(f"{i:3d}. [{status_symbol}] {file_path}")
        i += 1

    print("\nCommands:")
    print("  <number>     - Toggle file selection")
    print("  a           - Select all")
    print("  u           - Unselect all")
    print("  q           - Quit without staging")
    print("  s           - Stage selected files and quit")

    while True:
        try:
            choice = input("\n> ").strip().lower()

            if choice == "q":
                return set()
            elif choice == "s":
                return selected
            elif choice == "a":
                selected = {f[0] for f in files}
                print(f"Selected {len(selected)} file(s)")
            elif choice == "u":
                selected = set()
                print("Unselected all files")
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    file_path, _ = files[idx]
                    if file_path in selected:
                        selected.remove(file_path)
                        print(f"Unselected: {file_path}")
                    else:
                        selected.add(file_path)
                        print(f"Selected: {file_path}")
                else:
                    print("Invalid number")
            else:
                print("Invalid command")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled")
            return set()
