"""
Parallel processing utilities for ugit.

Provides concurrent file processing for better performance.
"""

import concurrent.futures
from typing import Callable, Iterable, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def process_parallel(
    items: Iterable[T], func: Callable[[T], R], max_workers: int = 4
) -> List[R]:
    """
    Process items in parallel.

    Args:
        items: Items to process
        func: Function to apply to each item
        max_workers: Maximum number of worker threads

    Returns:
        List of results
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func, item) for item in items]
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                # Continue processing other items even if one fails
                # Log error but don't fail entire operation
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Error processing item in parallel: {e}")
        return results
