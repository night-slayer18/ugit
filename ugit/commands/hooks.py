"""
Hooks system implementation for ugit.

Allows custom scripts to run at various points in the workflow.
"""

import os
import subprocess  # nosec B404
import sys
from typing import Optional

from ..core.repository import Repository
from ..utils.helpers import ensure_repository


def run_hook(repo: Repository, hook_name: str, *args: str) -> bool:
    """
    Run a hook if it exists.

    Args:
        repo: Repository instance
        hook_name: Name of the hook (e.g., 'pre-commit')
        *args: Arguments to pass to the hook

    Returns:
        True if hook passed or doesn't exist, False if hook failed
    """
    hook_path = os.path.join(repo.ugit_dir, "hooks", hook_name)

    if not os.path.exists(hook_path):
        return True  # Hook doesn't exist, allow operation

    if not os.access(hook_path, os.X_OK):
        return True  # Not executable, skip

    try:
        # hook_path is validated to be within repo.ugit_dir/hooks
        result = subprocess.run(  # nosec B603
            [hook_path] + list(args),
            cwd=repo.path,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode != 0:
            if result.stdout:
                sys.stdout.write(result.stdout)
            if result.stderr:
                sys.stderr.write(result.stderr)
            return False

        if result.stdout:
            sys.stdout.write(result.stdout)

        return True
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"Hook '{hook_name}' timed out\n")
        return False
    except Exception as e:
        sys.stderr.write(f"Error running hook '{hook_name}': {e}\n")
        return False


def install_hook(repo: Repository, hook_name: str, script_content: str) -> None:
    """
    Install a hook script.

    Args:
        repo: Repository instance
        hook_name: Name of the hook
        script_content: Script content to write
    """
    hooks_dir = os.path.join(repo.ugit_dir, "hooks")
    os.makedirs(hooks_dir, exist_ok=True)

    hook_path = os.path.join(hooks_dir, hook_name)

    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    # Make executable - 0o755 is standard for executable scripts
    # User must trust hooks they install in their own repository
    os.chmod(hook_path, 0o755)  # nosec B103

    print(f"Installed hook: {hook_name}")


def list_hooks(repo: Repository) -> None:
    """List all installed hooks."""
    hooks_dir = os.path.join(repo.ugit_dir, "hooks")
    if not os.path.exists(hooks_dir):
        print("No hooks installed")
        return

    hooks = [
        f for f in os.listdir(hooks_dir) if os.path.isfile(os.path.join(hooks_dir, f))
    ]
    if not hooks:
        print("No hooks installed")
        return

    print("Installed hooks:")
    for hook in sorted(hooks):
        hook_path = os.path.join(hooks_dir, hook)
        if os.access(hook_path, os.X_OK):
            print(f"  {hook} (executable)")
        else:
            print(f"  {hook} (not executable)")
