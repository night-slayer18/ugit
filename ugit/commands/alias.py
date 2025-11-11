"""
Alias command implementation for ugit.

Allows users to create custom command shortcuts.
"""

from typing import Optional

from ..utils.config import Config
from ..utils.helpers import ensure_repository


def alias(
    name: Optional[str] = None,
    command: Optional[str] = None,
    list_aliases: bool = False,
) -> None:
    """
    Manage command aliases.

    Args:
        name: Alias name
        command: Command to alias
        list_aliases: List all aliases
    """
    repo = ensure_repository()
    config = Config(repo.path)

    if list_aliases:
        _list_aliases(config)
    elif name and command:
        _set_alias(config, name, command)
    elif name:
        _show_alias(config, name)
    else:
        _list_aliases(config)


def _set_alias(config: Config, name: str, command: str) -> None:
    """Set an alias."""
    config.set("alias", name, command)
    print(f"Alias '{name}' set to '{command}'")


def _show_alias(config: Config, name: str) -> None:
    """Show an alias."""
    alias_cmd = config.get("alias", name)
    if alias_cmd:
        print(alias_cmd)
    else:
        print(f"Alias '{name}' not found")


def _list_aliases(config: Config) -> None:
    """List all aliases."""
    all_settings = config.get_all_settings()
    aliases = {k: v for k, v in all_settings.items() if k.startswith("alias.")}

    if not aliases:
        print("No aliases defined")
        return

    for key, value in sorted(aliases.items()):
        alias_name = key.replace("alias.", "")
        print(f"{alias_name}\t{value}")


def expand_alias(config: Config, command: str) -> str:
    """
    Expand alias if it exists.

    Args:
        config: Config instance
        command: Command to check for alias

    Returns:
        Expanded command or original if no alias
    """
    alias_cmd = config.get("alias", command)
    return alias_cmd if alias_cmd else command
