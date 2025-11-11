"""
Add files to the staging area.
"""

import os
import sys
from typing import Dict, List, Tuple, Union

from ..core.exceptions import UgitError
from ..core.objects import hash_object
from ..core.repository import Index
from ..utils.helpers import (
    ensure_repository,
    get_ignored_patterns,
    safe_read_file,
    should_ignore_file,
)
from ..utils.parallel import process_parallel
from ..utils.validation import sanitize_path, validate_path


def add(paths: Union[str, List[str]]) -> None:
    """
    Add file(s) to the staging area. This function reads the index once,
    updates it in memory, and writes it back once at the end.

    Args:
        paths: File or directory paths to add (string or list of strings)

    Raises:
        UgitError: If path validation fails
    """
    repo = ensure_repository()
    index = Index(repo)
    index_data = index.read()
    ignored_patterns = get_ignored_patterns(repo.path)

    if isinstance(paths, str):
        paths = [paths]

    # Validate all paths before processing
    validated_paths = []
    for path in paths:
        try:
            # Sanitize and validate path
            sanitized = sanitize_path(path)
            if validate_path(sanitized, base_path=repo.path):
                validated_paths.append(sanitized)
            else:
                raise UgitError(f"Invalid or unsafe path: {path}")
        except ValueError as e:
            raise UgitError(f"Invalid path '{path}': {e}") from e

    # Track if any changes are made to the index and collect messages for user
    changes_made = False
    messages: List[str] = []

    # Use parallel processing for large numbers of files
    if len(validated_paths) > 10:
        # Process files in parallel
        results = process_parallel(
            validated_paths,
            lambda path: _add_single_path(path, index_data, ignored_patterns, []),
            max_workers=4,
        )
        changes_made = any(results)
    else:
        # Sequential processing for small numbers
        for file_path in validated_paths:
            if _add_single_path(file_path, index_data, ignored_patterns, messages):
                changes_made = True

    if changes_made:
        index.write(index_data)
        # Print messages to stdout for user visibility
        for m in messages:
            print(m)


def _add_single_path(
    path: str,
    index_data: Dict[str, Tuple[str, float, int]],
    ignored_patterns: List[str],
    messages: List[str],
) -> bool:
    """
    Add a single file or directory to the in-memory index, handling deletions.
    Returns True if the index was modified.
    """
    change_detected = False
    if not os.path.exists(path):
        # Path doesn't exist, check if it was a tracked file (a deletion)
        try:
            rel_path = os.path.relpath(path)
            if rel_path in index_data:
                del index_data[rel_path]
                change_detected = True
                messages.append(f"deleted: {rel_path}")
            else:
                print(
                    f"Error: '{path}' does not exist and is not tracked.",
                    file=sys.stderr,
                )
        except ValueError:
            print(f"Error: '{path}' does not exist.", file=sys.stderr)
        return change_detected

    if os.path.isdir(path):
        # Recursively add files and handle deletions
        all_tracked_files = set(index_data.keys())
        normalized_path = os.path.normpath(path)

        if normalized_path == ".":
            tracked_files_in_dir = all_tracked_files
        else:
            tracked_files_in_dir = {
                p
                for p in all_tracked_files
                if os.path.normpath(p).startswith(normalized_path + os.sep)
                or os.path.normpath(p) == normalized_path
            }

        existing_files_in_dir = set()

        for root, dirs, files in os.walk(path):
            if ".ugit" in dirs:
                dirs.remove(".ugit")

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path)

                if should_ignore_file(rel_path, ignored_patterns):
                    continue

                existing_files_in_dir.add(rel_path)
                if _add_single_file(file_path, index_data, messages):
                    change_detected = True

        # Find and stage deletions
        deleted_files = tracked_files_in_dir - existing_files_in_dir
        for file_to_delete in deleted_files:
            del index_data[file_to_delete]
            change_detected = True
            messages.append(f"deleted: {file_to_delete}")

    else:  # It's a file
        rel_path = os.path.relpath(path)
        if should_ignore_file(rel_path, ignored_patterns):
            pass
        elif _add_single_file(path, index_data, messages):
            change_detected = True

    return change_detected


def _add_single_file(
    path: str, index_data: Dict[str, Tuple[str, float, int]], messages: List[str]
) -> bool:
    """
    Add a single file to the in-memory index if it has changed.
    Returns True if the index was updated.
    """
    try:
        stat = os.stat(path)
        data = safe_read_file(path)
        new_sha = hash_object(data, "blob")

        rel_path = os.path.relpath(path)
        normalized_path = os.path.normpath(rel_path).replace(os.sep, "/")

        current_entry = index_data.get(normalized_path)
        if current_entry and current_entry[0] == new_sha:
            return False  # SHA is the same, no need to update

        index_data[normalized_path] = (new_sha, stat.st_mtime, stat.st_size)
        # Determine whether this was an add or update
        if current_entry:
            messages.append(f"updated: {normalized_path}")
        else:
            messages.append(f"added: {normalized_path}")
        return True

    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error adding file '{path}': {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error adding file '{path}': {e}", file=sys.stderr)
        return False
