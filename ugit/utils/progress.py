"""
Progress indicator utilities for ugit.

Provides progress bars and indicators for long-running operations.
"""

import sys
from typing import Any, Iterator, Optional


class ProgressBar:
    """Simple progress bar implementation."""

    def __init__(self, total: int, description: str = "Progress", width: int = 50):
        """
        Initialize progress bar.

        Args:
            total: Total number of items
            description: Description text
            width: Width of progress bar in characters
        """
        self.total = total
        self.current = 0
        self.description = description
        self.width = width

    def update(self, n: int = 1) -> None:
        """
        Update progress by n items.

        Args:
            n: Number of items to add
        """
        self.current = min(self.current + n, self.total)
        self._display()

    def _display(self) -> None:
        """Display progress bar."""
        if self.total == 0:
            percent = 100
        else:
            percent = int(100 * self.current / self.total)

        filled = (
            int(self.width * self.current / self.total)
            if self.total > 0
            else self.width
        )
        bar = "=" * filled + "-" * (self.width - filled)

        sys.stdout.write(
            f"\r{self.description}: [{bar}] {percent}% ({self.current}/{self.total})"
        )
        sys.stdout.flush()

    def finish(self) -> None:
        """Finish progress bar."""
        self.current = self.total
        self._display()
        sys.stdout.write("\n")
        sys.stdout.flush()


def show_progress(
    iterable: Any, description: str = "Processing", total: Optional[int] = None
) -> Iterator[Any]:
    """
    Show progress while iterating.

    Args:
        iterable: Items to iterate over
        description: Description text
        total: Total number of items (if not provided, tries to get len())

    Yields:
        Items from iterable
    """
    if total is None:
        try:
            total = len(iterable)
        except TypeError:
            total = None

    if total is not None:
        bar = ProgressBar(total, description)
        for item in iterable:
            yield item
            bar.update()
        bar.finish()
    else:
        # No progress bar if we can't determine total
        for item in iterable:
            yield item
