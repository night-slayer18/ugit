#!/usr/bin/env python3
"""
Test runner for ugit.
"""

import os
import sys
import unittest

# Add the ugit directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def run_tests():
    """Run all ugit tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    test_dir = os.path.dirname(__file__)
    suite = loader.discover(test_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
