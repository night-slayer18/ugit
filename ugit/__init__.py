"""
ugit - A minimal Git implementation in Python

ugit is a simplified version control system that demonstrates the core concepts
of Git including object storage, staging, committing, and basic history.
"""

# Version is managed by setuptools_scm at build time (writes ugit/_version.py).
# Prefer the installed distribution metadata when available, otherwise fall
# back to the setuptools_scm generated file, and finally to a safe fallback.
try:
    # Python 3.8+
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # Older Python: use the backport if available
    try:
        from importlib_metadata import PackageNotFoundError, version  # type: ignore[import]
    except ImportError:
        version = None
        PackageNotFoundError = Exception  # type: ignore[misc,assignment]

__version__ = "0+unknown"
if version is not None:
    try:
        # If package is installed, this returns the distribution version (preferred).
        __version__ = version("ugit")
    except PackageNotFoundError:
        # Not installed into the environment — fall back to generated file.
        try:
            from ._version import __version__  # type: ignore
        except Exception:
            __version__ = "0+unknown"
else:
    # If importlib.metadata/importlib_metadata not available, still try the generated file.
    try:
        from ._version import __version__  # type: ignore
    except Exception:
        __version__ = "0+unknown"

__author__ = "night-slayer18"

__all__ = ["__version__", "__author__"]
