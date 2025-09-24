"""
Add files to the staging area.
"""

import fnmatch
import os
from typing import List, Union

from ..core.objects import hash_object
from ..core.repository import Index
from ..utils.helpers import ensure_repository, get_ignored_patterns, safe_read_file


def add(paths: Union[str, List[str]]) -> None:
    """
    Add file(s) to the staging area.

    Args:
        paths: File path or list of paths to add
    """
    repo = ensure_repository()
    index = Index(repo)
    ignored_patterns = get_ignored_patterns(repo.path)

    # Handle both single path and list of paths
    if isinstance(paths, str):
        paths = [paths]

    for file_path in paths:
        _add_single_path(file_path, index, ignored_patterns)


def _add_single_path(path: str, index: Index, ignored_patterns: List[str]) -> None:
    """Add a single file or directory to the index."""
    if not os.path.exists(path):
        print(f"Error: '{path}' does not exist")
        return

    if os.path.isdir(path):
        # Recursively add all files in directory
        added_count = 0
        ignored_count = 0

        for root, dirs, files in os.walk(path):
            # Skip .ugit directory
            if ".ugit" in dirs:
                dirs.remove(".ugit")

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path)

                if _should_ignore_file(rel_path, ignored_patterns):
                    ignored_count += 1
                    continue

                if _add_single_file(file_path, index):
                    added_count += 1

        if added_count > 0:
            print(f"Added {added_count} files from directory '{path}'")
        if ignored_count > 0:
            print(f"Ignored {ignored_count} files (see .ugitignore)")
        if added_count == 0 and ignored_count == 0:
            print(f"No files added from directory '{path}'")
    else:
        rel_path = os.path.relpath(path)
        if _should_ignore_file(rel_path, ignored_patterns):
            print(f"Ignored '{path}' (see .ugitignore)")
        else:
            _add_single_file(path, index)


def _add_single_file(path: str, index: Index) -> bool:
    """
    Add a single file to the index.

    Returns:
        True if file was successfully added, False otherwise
    """
    try:
        data = safe_read_file(path)
        sha = hash_object(data, "blob")
        index.add_file(path, sha)
        print(f"Staged {path} ({sha[:7]})")
        return True

    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error adding file '{path}': {e}")
        return False
    except Exception as e:
        print(f"Unexpected error adding file '{path}': {e}")
        return False


def _should_ignore_file(file_path: str, ignored_patterns: List[str]) -> bool:
    """Check if a file should be ignored based on patterns."""
    for pattern in ignored_patterns:
        # Check full path and just filename
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
            os.path.basename(file_path), pattern
        ):
            return True

        # Check if any parent directory matches the pattern
        path_parts = file_path.split(os.sep)
        for part in path_parts[:-1]:  # Exclude the filename itself
            if fnmatch.fnmatch(part, pattern):
                return True

    return False
