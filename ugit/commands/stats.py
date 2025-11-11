"""
Stats command implementation for ugit.

Show repository statistics and object counts.
"""

import os
from typing import Dict

from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data


def stats() -> None:
    """Display repository statistics."""
    repo = ensure_repository()

    stats_data = _collect_stats(repo)
    _print_stats(stats_data)


def _collect_stats(repo: Repository) -> Dict:
    """Collect repository statistics."""
    stats = {
        "commits": 0,
        "branches": 0,
        "tags": 0,
        "objects": 0,
        "files": 0,
        "size": 0,
    }

    # Count commits
    head_sha = repo.get_head_ref()
    if head_sha:
        visited = set()
        stack = [head_sha]
        while stack:
            sha = stack.pop()
            if sha in visited or not sha:
                continue
            visited.add(sha)
            stats["commits"] += 1

            try:
                commit_data = get_commit_data(sha, repo=repo)
                if "parent" in commit_data and commit_data["parent"]:
                    stack.append(commit_data["parent"])
                if "parents" in commit_data:
                    stack.extend(p for p in commit_data["parents"] if p)
            except ValueError:
                pass

    # Count branches
    heads_dir = os.path.join(repo.ugit_dir, "refs", "heads")
    if os.path.exists(heads_dir):
        stats["branches"] = len(
            [
                f
                for f in os.listdir(heads_dir)
                if os.path.isfile(os.path.join(heads_dir, f))
            ]
        )

    # Count tags
    tags_dir = os.path.join(repo.ugit_dir, "refs", "tags")
    if os.path.exists(tags_dir):
        stats["tags"] = len(
            [
                f
                for f in os.listdir(tags_dir)
                if os.path.isfile(os.path.join(tags_dir, f))
            ]
        )

    # Count objects and calculate size
    objects_dir = os.path.join(repo.ugit_dir, "objects")
    if os.path.exists(objects_dir):
        for root, dirs, files in os.walk(objects_dir):
            for file in files:
                file_path = os.path.join(root, file)
                stats["objects"] += 1
                try:
                    stats["size"] += os.path.getsize(file_path)
                except OSError:
                    pass

    # Count files in index
    from ..core.repository import Index

    index = Index(repo)
    index_data = index.read()
    stats["files"] = len(index_data)

    return stats


def _print_stats(stats: Dict) -> None:
    """Print statistics in a readable format."""
    print("Repository Statistics:")
    print(f"  Commits: {stats['commits']}")
    print(f"  Branches: {stats['branches']}")
    print(f"  Tags: {stats['tags']}")
    print(f"  Objects: {stats['objects']}")
    print(f"  Tracked files: {stats['files']}")
    print(f"  Repository size: {_format_size(stats['size'])}")


def _format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    size: float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"
