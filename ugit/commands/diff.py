"""
Diff command implementation for ugit.

This module handles comparing files between different states:
- Working directory vs staging area
- Staging area vs last commit
- Between two commits
"""

import os
import difflib
from typing import Dict, List, Optional, Tuple

from ..core.objects import get_object, object_exists
from ..core.repository import Repository
from ..utils.helpers import get_ignored_patterns


def diff(staged: bool = False, commit1: str = None, commit2: str = None) -> None:
    """
    Show differences between files.
    
    Args:
        staged: Show differences between staging area and last commit
        commit1: First commit to compare (if comparing commits)
        commit2: Second commit to compare (if comparing commits)
    """
    repo = Repository()
    if not repo.is_repository():
        print("Not in a ugit repository")
        return
    
    if commit1 and commit2:
        _diff_commits(repo, commit1, commit2)
    elif staged:
        _diff_staged(repo)
    else:
        _diff_working_directory(repo)


def _diff_working_directory(repo: Repository) -> None:
    """Show differences between working directory and staging area."""
    # Get staged files
    staged_files = _get_staged_files(repo)
    
    # Get working directory files
    working_files = _get_working_files(repo)
    
    # Compare files
    all_files = set(staged_files.keys()) | set(working_files.keys())
    
    has_changes = False
    for file_path in sorted(all_files):
        staged_content = staged_files.get(file_path, "")
        working_content = working_files.get(file_path, "")
        
        if staged_content != working_content:
            has_changes = True
            _print_file_diff(file_path, staged_content, working_content, "staged", "working")
    
    if not has_changes:
        print("No changes in working directory")


def _diff_staged(repo: Repository) -> None:
    """Show differences between staging area and last commit."""
    # Get last commit
    head_commit = repo.get_head_ref()
    if not head_commit:
        print("No commits yet")
        return
    
    # Get committed files
    committed_files = _get_commit_files(repo, head_commit)
    
    # Get staged files
    staged_files = _get_staged_files(repo)
    
    # Compare files
    all_files = set(committed_files.keys()) | set(staged_files.keys())
    
    has_changes = False
    for file_path in sorted(all_files):
        committed_content = committed_files.get(file_path, "")
        staged_content = staged_files.get(file_path, "")
        
        if committed_content != staged_content:
            has_changes = True
            _print_file_diff(file_path, committed_content, staged_content, "committed", "staged")
    
    if not has_changes:
        print("No changes staged for commit")


def _diff_commits(repo: Repository, commit1: str, commit2: str) -> None:
    """Show differences between two commits."""
    # Get files from both commits
    try:
        files1 = _get_commit_files(repo, commit1)
        files2 = _get_commit_files(repo, commit2)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return
    
    # Compare files
    all_files = set(files1.keys()) | set(files2.keys())
    
    has_changes = False
    for file_path in sorted(all_files):
        content1 = files1.get(file_path, "")
        content2 = files2.get(file_path, "")
        
        if content1 != content2:
            has_changes = True
            _print_file_diff(file_path, content1, content2, commit1[:7], commit2[:7])
    
    if not has_changes:
        print("No differences between commits")


def _get_staged_files(repo: Repository) -> Dict[str, str]:
    """Get all staged files and their content."""
    index_path = os.path.join(repo.ugit_dir, "index")
    staged_files = {}
    
    if not os.path.exists(index_path):
        return staged_files
    
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split("\t")
                if len(parts) >= 2:
                    file_path = parts[1]
                    sha = parts[0]
                    
                    try:
                        obj_type, content = get_object(sha)
                        if obj_type == "blob":
                            staged_files[file_path] = content.decode("utf-8", errors="replace")
                    except (FileNotFoundError, ValueError, UnicodeDecodeError):
                        staged_files[file_path] = ""
    except (IOError, OSError):
        pass
    
    return staged_files


def _get_working_files(repo: Repository) -> Dict[str, str]:
    """Get all working directory files and their content."""
    working_files = {}
    ignored_patterns = get_ignored_patterns(repo.path)
    
    for root, dirs, files in os.walk(repo.path):
        # Skip .ugit directory
        if ".ugit" in dirs:
            dirs.remove(".ugit")
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo.path)
            
            # Skip ignored files
            if _should_ignore_file(rel_path, ignored_patterns):
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    working_files[rel_path] = f.read()
            except (IOError, OSError, UnicodeDecodeError):
                working_files[rel_path] = ""
    
    return working_files


def _get_commit_files(repo: Repository, commit_sha: str) -> Dict[str, str]:
    """Get all files from a specific commit."""
    try:
        # Get commit object
        commit_type, commit_data = get_object(commit_sha)
        if commit_type != "commit":
            raise ValueError(f"Object {commit_sha} is not a commit")
        
        # Parse commit to get tree
        commit_lines = commit_data.decode("utf-8").split("\n")
        tree_line = next((line for line in commit_lines if line.startswith("tree ")), None)
        if not tree_line:
            raise ValueError("Commit has no tree")
        
        tree_sha = tree_line.split()[1]
        
        # Get files from tree
        return _get_tree_files(tree_sha)
        
    except (FileNotFoundError, ValueError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid commit {commit_sha}: {e}")


def _get_tree_files(tree_sha: str, prefix: str = "") -> Dict[str, str]:
    """Recursively get all files from a tree object."""
    try:
        tree_type, tree_data = get_object(tree_sha)
        if tree_type != "tree":
            raise ValueError(f"Object {tree_sha} is not a tree")
        
        files = {}
        i = 0
        
        while i < len(tree_data):
            # Find null terminator for mode and name
            null_pos = tree_data.index(b"\x00", i)
            mode_name = tree_data[i:null_pos].decode("utf-8")
            
            # Extract 20-byte SHA after null
            sha_bytes = tree_data[null_pos + 1:null_pos + 21]
            if len(sha_bytes) != 20:
                break
            
            sha = sha_bytes.hex()
            mode, name = mode_name.split(" ", 1)
            full_path = os.path.join(prefix, name) if prefix else name
            
            if mode == "40000":  # Directory
                # Recursively get files from subdirectory
                subfiles = _get_tree_files(sha, full_path)
                files.update(subfiles)
            else:  # File
                try:
                    obj_type, content = get_object(sha)
                    if obj_type == "blob":
                        files[full_path] = content.decode("utf-8", errors="replace")
                except (FileNotFoundError, ValueError, UnicodeDecodeError):
                    files[full_path] = ""
            
            i = null_pos + 21
        
        return files
        
    except (FileNotFoundError, ValueError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid tree {tree_sha}: {e}")


def _print_file_diff(file_path: str, content1: str, content2: str, label1: str, label2: str) -> None:
    """Print unified diff for a file."""
    lines1 = content1.splitlines(keepends=True)
    lines2 = content2.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=f"{label1}/{file_path}",
        tofile=f"{label2}/{file_path}",
        lineterm=""
    )
    
    diff_output = list(diff)
    if diff_output:
        print(f"\n--- {file_path}")
        for line in diff_output:
            if line.startswith("+++") or line.startswith("---"):
                print(line)
            elif line.startswith("@@"):
                print(f"\033[36m{line}\033[0m")  # Cyan
            elif line.startswith("+"):
                print(f"\033[32m{line}\033[0m")  # Green
            elif line.startswith("-"):
                print(f"\033[31m{line}\033[0m")  # Red
            else:
                print(line, end="")


def _should_ignore_file(file_path: str, ignored_patterns: List[str]) -> bool:
    """Check if a file should be ignored based on patterns."""
    import fnmatch
    
    for pattern in ignored_patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
    
    return False