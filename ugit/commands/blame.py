"""
Blame command implementation for ugit.

Shows who last modified each line of a file.
"""

import os
from typing import Dict, List, Optional, Set, Tuple

from ..core.exceptions import InvalidRefError, UgitError
from ..core.objects import get_object
from ..core.repository import Repository
from ..utils.helpers import (
    ensure_repository,
    get_commit_data,
    get_tree_entries,
    safe_read_file,
)
from ..utils.validation import validate_sha


def blame(
    file_path: str, commit: Optional[str] = None, line_numbers: bool = True
) -> None:
    """
    Show blame information for a file.

    Args:
        file_path: Path to the file
        commit: Commit to blame (default: HEAD)
        line_numbers: Show line numbers
    """
    repo = ensure_repository()

    if commit is None:
        commit = repo.get_head_ref()
        if not commit:
            raise UgitError("No commits in repository")
    elif not validate_sha(commit):
        raise InvalidRefError(f"Invalid commit SHA: {commit}")

    try:
        blame_data = _get_blame_data(repo, file_path, commit)
        _print_blame(blame_data, file_path, line_numbers)
    except (FileNotFoundError, ValueError) as e:
        raise UgitError(f"Cannot blame file '{file_path}': {e}")


def _get_blame_data(
    repo: Repository, file_path: str, commit_sha: str
) -> List[Tuple[str, str, int, str]]:
    """
    Get blame data for a file.

    Returns:
        List of tuples: (commit_sha, author, line_number, line_content)
    """
    # Get file content at commit
    try:
        commit_data = get_commit_data(commit_sha, repo=repo)
        tree_sha = commit_data["tree"]
        file_sha = _get_file_sha_from_tree(repo, tree_sha, file_path)

        if not file_sha:
            raise FileNotFoundError(
                f"File '{file_path}' not found in commit {commit_sha[:7]}"
            )

        # Get file content
        obj_type, file_data = get_object(file_sha, repo=repo)
        if obj_type != "blob":
            raise ValueError(f"'{file_path}' is not a file")

        lines = file_data.decode("utf-8", errors="replace").splitlines()

    except (FileNotFoundError, ValueError, UnicodeDecodeError) as e:
        raise ValueError(f"Error reading file: {e}")

    # For each line, find when it was last modified
    blame_data = []
    visited_commits: Set[str] = set()

    for line_num, line_content in enumerate(lines, 1):
        commit_sha_for_line, author = _find_line_origin(
            repo, file_path, commit_sha, line_num, line_content, visited_commits
        )
        blame_data.append((commit_sha_for_line, author, line_num, line_content))

    return blame_data


def _find_line_origin(
    repo: Repository,
    file_path: str,
    commit_sha: str,
    line_num: int,
    line_content: str,
    visited: set,
) -> Tuple[str, str]:
    """
    Find the commit where a line was last modified.

    Returns:
        Tuple of (commit_sha, author)
    """
    current_sha = commit_sha
    visited.add(current_sha)

    while current_sha:
        try:
            commit_data = get_commit_data(current_sha, repo=repo)
            tree_sha = commit_data["tree"]
            file_sha = _get_file_sha_from_tree(repo, tree_sha, file_path)

            if not file_sha:
                # File didn't exist in this commit, check parent
                parent = commit_data.get("parent")
                if parent and parent not in visited:
                    current_sha = parent
                    visited.add(current_sha)
                    continue
                break

            # Get file content at this commit
            obj_type, file_data = get_object(file_sha, repo=repo)
            if obj_type != "blob":
                break

            lines = file_data.decode("utf-8", errors="replace").splitlines()
            if line_num <= len(lines) and lines[line_num - 1] == line_content:
                # Line exists and matches, check parent
                parent = commit_data.get("parent")
                if parent and parent not in visited:
                    current_sha = parent
                    visited.add(current_sha)
                    continue
                else:
                    # This is the commit where the line was introduced
                    author = commit_data.get("author", "Unknown")
                    return (current_sha, author)
            else:
                # Line doesn't match or doesn't exist, this commit modified it
                author = commit_data.get("author", "Unknown")
                return (current_sha, author)

        except (ValueError, FileNotFoundError, KeyError):
            # Move to parent on error
            try:
                commit_data = get_commit_data(current_sha, repo=repo)
                parent = commit_data.get("parent")
                if parent and parent not in visited:
                    current_sha = parent
                    visited.add(current_sha)
                    continue
            except (ValueError, KeyError):
                pass
            break

    # Fallback to current commit
    try:
        commit_data = get_commit_data(commit_sha, repo=repo)
        author = commit_data.get("author", "Unknown")
        return (commit_sha, author)
    except ValueError:
        return (commit_sha, "Unknown")


def _get_file_sha_from_tree(
    repo: Repository, tree_sha: str, file_path: str
) -> Optional[str]:
    """Get file SHA from tree object."""
    try:
        entries = get_tree_entries(tree_sha, repo=repo)
        for mode, path, sha in entries:
            if path == file_path:
                return sha
    except ValueError:
        pass
    return None


def _print_blame(
    blame_data: List[Tuple[str, str, int, str]], file_path: str, line_numbers: bool
) -> None:
    """Print blame output."""
    for commit_sha, author, line_num, line_content in blame_data:
        # Extract author name (before <email>)
        author_name = author.split("<")[0].strip() if "<" in author else author

        if line_numbers:
            print(f"{commit_sha[:7]:7} {line_num:4} {author_name:20} {line_content}")
        else:
            print(f"{commit_sha[:7]:7} {author_name:20} {line_content}")
