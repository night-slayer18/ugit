"""
ugit - A minimal Git implementation in Python

ugit is a simplified version control system that demonstrates the core concepts
of Git including object storage, staging, committing, and basic history.
"""

from importlib.metadata import PackageNotFoundError, version

__author__ = "night-slayer18"

try:
    __version__ = version("ugit")
except PackageNotFoundError:
    # Package is not installed
    __version__ = "unknown"

__all__ = ["__version__", "__author__"]
