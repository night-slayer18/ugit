"""
Commit template support for ugit.

Allows users to define commit message templates.
"""

import os
from typing import Optional

from ..core.repository import Repository
from ..utils.helpers import ensure_repository


def get_commit_template(repo: Optional[Repository] = None) -> Optional[str]:
    """
    Get commit message template.

    Args:
        repo: Repository instance (optional)

    Returns:
        Template content or None
    """
    if repo is None:
        from ..utils.helpers import ensure_repository

        repo = ensure_repository()

    # Check repository config first
    from ..utils.config import Config

    config = Config(repo.path)
    template_path = config.get("commit", "template")

    if template_path:
        if os.path.isabs(template_path):
            full_path = template_path
        else:
            full_path = os.path.join(repo.path, template_path)

        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            except (IOError, OSError):
                pass

    # Check default template location
    default_template = os.path.join(repo.ugit_dir, "COMMIT_TEMPLATE")
    if os.path.exists(default_template):
        try:
            with open(default_template, "r", encoding="utf-8") as f:
                return f.read()
        except (IOError, OSError):
            pass

    return None


def set_commit_template(repo: Repository, template_path: str) -> None:
    """
    Set commit message template.

    Args:
        repo: Repository instance
        template_path: Path to template file
    """
    from ..utils.config import Config

    config = Config(repo.path)
    config.set("commit", "template", template_path)
    print(f"Set commit template to: {template_path}")
