"""
Grep command implementation for ugit.

Search for content across the repository.
"""

import os
import re
from typing import List, Optional, Pattern

from ..core.exceptions import UgitError
from ..core.objects import get_object
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data, get_tree_entries
from ..utils.validation import validate_sha


def grep(
    pattern: str,
    path: Optional[str] = None,
    commit: Optional[str] = None,
    case_insensitive: bool = False,
    recursive: bool = True,
) -> None:
    """
    Search for pattern in repository files.

    Args:
        pattern: Search pattern (regex)
        path: Path to search in (default: current directory)
        commit: Commit to search in (default: HEAD)
        case_insensitive: Case-insensitive search
        recursive: Search recursively
    """
    repo = ensure_repository()

    if commit is None:
        commit = repo.get_head_ref()
        if not commit:
            raise UgitError("No commits in repository")
    elif not validate_sha(commit):
        raise UgitError(f"Invalid commit SHA: {commit}")

    # Compile pattern
    flags = re.IGNORECASE if case_insensitive else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        raise UgitError(f"Invalid regex pattern: {e}")

    # Get commit tree
    try:
        commit_data = get_commit_data(commit, repo=repo)
        tree_sha = commit_data["tree"]
    except ValueError as e:
        raise UgitError(f"Invalid commit: {e}")

    # Search in tree
    matches = _search_tree(repo, tree_sha, regex, path or ".", recursive)

    # Print results
    for file_path, line_num, line_content in matches:
        print(f"{file_path}:{line_num}:{line_content}")


def _search_tree(
    repo: Repository,
    tree_sha: str,
    pattern: Pattern[str],
    base_path: str,
    recursive: bool,
) -> List[tuple]:
    """Search for pattern in tree."""
    matches = []

    try:
        entries = get_tree_entries(tree_sha, repo=repo)
        for mode, path, sha in entries:
            # Check if path matches base_path filter
            if base_path != "." and not path.startswith(base_path):
                continue

            if mode.startswith("10"):  # File
                try:
                    obj_type, content = get_object(sha, repo=repo)
                    if obj_type == "blob":
                        # Search in file content
                        try:
                            text = content.decode("utf-8", errors="replace")
                            for line_num, line in enumerate(text.splitlines(), 1):
                                if pattern.search(line):
                                    matches.append((path, line_num, line.strip()))
                        except UnicodeDecodeError:
                            # Skip binary files
                            pass
                except (FileNotFoundError, ValueError):
                    pass
            elif mode.startswith("40") and recursive:  # Directory
                # Recursively search subdirectory
                sub_matches = _search_tree(repo, sha, pattern, base_path, recursive)
                matches.extend(sub_matches)
    except ValueError:
        pass

    return matches
