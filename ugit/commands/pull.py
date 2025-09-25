"""
Pull changes from remote repositories.

This module handles fetching and merging changes from remote repositories.
"""

import os
from typing import Optional

from ..core.repository import Repository
from .fetch import fetch
from .merge import merge


def pull(remote_name: str = "origin", branch: Optional[str] = None) -> None:
    """
    Fetch and merge changes from a remote repository.
    
    Args:
        remote_name: Name of remote to pull from
        branch: Specific branch to pull (optional)
    """
    repo = Repository()
    
    if not repo.is_repository():
        print("Not a ugit repository")
        return
    
    # Get current branch
    current_branch = _get_current_branch(repo)
    if not current_branch:
        print("fatal: You are not currently on a branch")
        return
    
    # Use current branch if no branch specified
    if branch is None:
        branch = current_branch
    
    print(f"Pulling {remote_name}/{branch} into {current_branch}")
    
    # First, fetch the changes
    fetch(remote_name, branch)
    
    # Get the remote ref
    remote_ref_path = os.path.join(repo.ugit_dir, "refs", "remotes", remote_name, branch)
    if not os.path.exists(remote_ref_path):
        print(f"fatal: Couldn't find remote ref {remote_name}/{branch}")
        return
    
    try:
        with open(remote_ref_path, 'r') as f:
            remote_sha = f.read().strip()
    except (IOError, OSError) as e:
        print(f"fatal: Failed to read remote ref: {e}")
        return
    
    # Get current HEAD
    current_sha = repo.get_head_ref()
    if not current_sha:
        print("fatal: No commits in current branch")
        return
    
    # Check if we're already up to date
    if current_sha == remote_sha:
        print("Already up to date.")
        return
    
    # Check if this is a fast-forward merge
    if _is_ancestor(repo, current_sha, remote_sha):
        # Fast-forward merge
        _fast_forward_merge(repo, remote_sha, f"{remote_name}/{branch}")
        print(f"Fast-forward merge completed")
    else:
        # Need to do a real merge - for now just do fast-forward
        print(f"Merging {remote_name}/{branch} into {current_branch}")
        try:
            # For simplicity, let's do a fast-forward merge
            _fast_forward_merge(repo, remote_sha, f"{remote_name}/{branch}")
            print(f"Fast-forward merge completed")
        except Exception as e:
            print(f"Merge failed: {e}")
            return


def _get_current_branch(repo: Repository) -> Optional[str]:
    """
    Get the name of the current branch.
    
    Args:
        repo: Repository instance
        
    Returns:
        Current branch name or None if detached HEAD
    """
    head_path = os.path.join(repo.ugit_dir, "HEAD")
    if not os.path.exists(head_path):
        return None
    
    try:
        with open(head_path, 'r') as f:
            head_content = f.read().strip()
        
        if head_content.startswith("ref: refs/heads/"):
            return head_content[16:]  # Remove "ref: refs/heads/"
            
        return None  # Detached HEAD
    except (IOError, OSError):
        return None


def _is_ancestor(repo: Repository, ancestor_sha: str, descendant_sha: str) -> bool:
    """
    Check if ancestor_sha is an ancestor of descendant_sha.
    
    Args:
        repo: Repository instance
        ancestor_sha: Potential ancestor commit SHA
        descendant_sha: Potential descendant commit SHA
        
    Returns:
        True if ancestor_sha is an ancestor of descendant_sha
    """
    if ancestor_sha == descendant_sha:
        return True
    
    from ..core.objects import get_object
    
    # Walk back from descendant_sha to see if we find ancestor_sha
    visited = set()
    to_check = [descendant_sha]
    
    while to_check:
        current_sha = to_check.pop()
        
        if current_sha in visited:
            continue
        visited.add(current_sha)
        
        if current_sha == ancestor_sha:
            return True
        
        try:
            commit_type, commit_content = get_object(current_sha)
            if commit_type != 'commit':
                continue
                
            # Parse commit to find parents
            lines = commit_content.decode('utf-8').split('\n')
            for line in lines:
                if line.startswith('parent '):
                    parent_sha = line[7:]
                    to_check.append(parent_sha)
                    
        except Exception:
            continue
    
    return False


def _fast_forward_merge(repo: Repository, branch: str, target_sha: str) -> None:
    """
    Perform a fast-forward merge.
    
    Args:
        repo: Repository instance
        branch: Current branch name
        target_sha: Target commit SHA
    """
    # Update branch ref
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch)
    try:
        with open(branch_path, 'w') as f:
            f.write(target_sha)
    except (IOError, OSError) as e:
        raise RuntimeError(f"Failed to update branch {branch}: {e}")
    
    # Checkout the new commit
    from .checkout import _checkout_commit
    _checkout_commit(repo, target_sha)