"""
Caching utilities for ugit.

Provides memoization and caching for expensive operations
like object lookups and tree traversals.
"""

from functools import lru_cache
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


class SimpleCache:
    """
    Simple in-memory cache with size limit.

    Useful for caching repository state and object lookups.
    """

    def __init__(self, max_size: int = 128):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self._cache: dict = {}
        self._access_order: list = []

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self._cache:
            # Update access order (move to end)
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove oldest item if cache is full
        if len(self._cache) >= self.max_size and self._access_order:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]

        self._cache[key] = value
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
        self._access_order.clear()

    def invalidate(self, key: str) -> None:
        """
        Remove specific key from cache.

        Args:
            key: Cache key to remove
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)


# Global cache instance for repository operations
_repo_cache: Optional[SimpleCache] = None


def get_repo_cache() -> SimpleCache:
    """
    Get the global repository cache instance.

    Returns:
        Global SimpleCache instance
    """
    global _repo_cache
    if _repo_cache is None:
        _repo_cache = SimpleCache(max_size=256)
    return _repo_cache


def clear_repo_cache() -> None:
    """Clear the global repository cache."""
    cache = get_repo_cache()
    cache.clear()


def memoize(maxsize: int = 128) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for memoizing function results.

    Args:
        maxsize: Maximum cache size

    Returns:
        Decorated function with memoization
    """
    return lru_cache(maxsize=maxsize)
