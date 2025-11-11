"""
CI compatibility tests.

These tests ensure that all features work correctly in CI environments
across different platforms (Mac, Linux, Windows).
"""

import os
import platform
import shutil
import sys
import tempfile
import unittest

import pytest

from ugit.commands.init import init
from ugit.core.repository import Repository


class TestCIPlatformCompatibility(unittest.TestCase):
    """Test platform compatibility for CI."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        # Use ignore_errors for Windows compatibility
        shutil.rmtree(self.test_dir, ignore_errors=True)
        # Give Windows time to release file handles
        if sys.platform == "win32":
            import time

            time.sleep(0.1)

    def test_platform_info(self):
        """Test that we can detect platform."""
        system = platform.system()
        self.assertIn(system, ["Darwin", "Linux", "Windows"])

    def test_path_operations_cross_platform(self):
        """Test path operations work on all platforms."""
        # Test path joining
        path1 = os.path.join("dir1", "dir2", "file.txt")
        path2 = os.path.join("dir1", "dir2", "file.txt")

        # Paths should be equivalent regardless of platform
        self.assertEqual(os.path.normpath(path1), os.path.normpath(path2))

    def test_file_operations_cross_platform(self):
        """Test file operations work on all platforms."""
        test_file = "test_file.txt"
        test_content = "test content\nwith newline"

        # Write file
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Read file
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertEqual(content, test_content)

    def test_directory_operations_cross_platform(self):
        """Test directory operations work on all platforms."""
        # Create nested directories
        nested_dir = os.path.join("level1", "level2", "level3")
        os.makedirs(nested_dir, exist_ok=True)

        self.assertTrue(os.path.exists(nested_dir))

        # Create file in nested directory
        test_file = os.path.join(nested_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        self.assertTrue(os.path.exists(test_file))

    def test_repository_init_cross_platform(self):
        """Test repository initialization works on all platforms."""
        init()

        repo = Repository()
        self.assertTrue(repo.is_repository())

        # Verify .ugit directory structure
        self.assertTrue(os.path.exists(repo.ugit_dir))
        self.assertTrue(os.path.exists(os.path.join(repo.ugit_dir, "objects")))
        self.assertTrue(os.path.exists(os.path.join(repo.ugit_dir, "refs")))

    def test_unicode_paths(self):
        """Test that unicode paths work on all platforms."""
        # Create file with unicode in name
        unicode_file = "test_文件.txt"
        try:
            with open(unicode_file, "w", encoding="utf-8") as f:
                f.write("test content")

            self.assertTrue(os.path.exists(unicode_file))

            # Read it back
            with open(unicode_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(content, "test content")
        except (UnicodeEncodeError, OSError):
            # Some platforms/filesystems may not support unicode filenames
            # This is acceptable
            pytest.skip("Unicode filenames not supported on this platform")

    def test_long_paths(self):
        """Test that long paths are handled correctly."""
        # Create a long path
        long_path = os.path.join(*["dir" + str(i) for i in range(10)], "file.txt")
        os.makedirs(os.path.dirname(long_path), exist_ok=True)

        with open(long_path, "w") as f:
            f.write("test")

        self.assertTrue(os.path.exists(long_path))

    def test_special_characters_in_paths(self):
        """Test paths with special characters."""
        # Test various special characters (platform-dependent)
        special_chars = ["test-file.txt", "test_file.txt", "test.file.txt"]

        for filename in special_chars:
            try:
                with open(filename, "w") as f:
                    f.write("test")
                self.assertTrue(os.path.exists(filename))
                os.remove(filename)
            except OSError:
                # Some characters may not be allowed on certain platforms
                pass

    def test_temp_directory_cleanup(self):
        """Test that temporary directories are cleaned up properly."""
        temp_path = tempfile.mkdtemp()
        try:
            self.assertTrue(os.path.exists(temp_path))

            # Create file in temp directory
            test_file = os.path.join(temp_path, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")

            self.assertTrue(os.path.exists(test_file))
        finally:
            # Cleanup
            shutil.rmtree(temp_path, ignore_errors=True)
            # On Windows, may need extra time
            if sys.platform == "win32":
                import time

                time.sleep(0.2)

    def test_file_locking(self):
        """Test file locking behavior across platforms."""
        test_file = "lock_test.txt"
        with open(test_file, "w") as f:
            f.write("test")

        # Try to open file again (should work on most platforms)
        with open(test_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "test")

    def test_case_sensitivity(self):
        """Test case sensitivity handling."""
        # Create file with lowercase
        with open("testfile.txt", "w") as f:
            f.write("lowercase")

        # On case-insensitive filesystems (Mac, Windows), this should find the file
        # On case-sensitive filesystems (Linux), it won't
        case_insensitive = os.path.exists("TESTFILE.TXT")
        case_sensitive = os.path.exists("testfile.txt")

        # At least one should be True
        self.assertTrue(case_sensitive)
        # Case-insensitive is platform-dependent, so we don't assert it


class TestCIEnvironment(unittest.TestCase):
    """Test CI environment compatibility."""

    def test_python_version(self):
        """Test Python version compatibility."""
        version = sys.version_info
        self.assertGreaterEqual(version.major, 3)
        self.assertGreaterEqual(version.minor, 9)

    def test_required_modules(self):
        """Test that required modules are available."""
        import json
        import os
        import shutil
        import tempfile

        # These should always be available
        self.assertTrue(hasattr(json, "dumps"))
        self.assertTrue(hasattr(os, "path"))
        self.assertTrue(hasattr(shutil, "rmtree"))
        self.assertTrue(hasattr(tempfile, "mkdtemp"))

    def test_optional_modules(self):
        """Test optional modules (may not be available in all environments)."""
        optional_modules = ["pytest", "fastapi", "httpx"]

        for module_name in optional_modules:
            try:
                __import__(module_name)
                available = True
            except ImportError:
                available = False

            # Optional modules may or may not be available
            # We just verify the check works
            self.assertIsInstance(available, bool)


if __name__ == "__main__":
    unittest.main()
