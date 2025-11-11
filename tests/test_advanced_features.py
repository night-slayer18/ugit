"""
Tests for advanced features that require more complex setup.

This includes:
- Interactive staging
- GPG signing (if available)
- HTTP remotes
- Web UI enhancements
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import pytest

from ugit.commands.add_interactive import add_interactive
from ugit.commands.alias import alias
from ugit.commands.gpg import has_gpg, sign_commit
from ugit.commands.init import init
from ugit.core.exceptions import UgitError
from ugit.core.repository import Repository


class TestAdvancedFeaturesBase(unittest.TestCase):
    """Base class for advanced features tests."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        init()
        from ugit.commands.config import config

        config("user.name", "Test User")
        config("user.email", "test@example.com")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)


class TestAliases(TestAdvancedFeaturesBase):
    """Test alias functionality."""

    def test_create_alias(self):
        """Test creating an alias."""
        # Create alias
        alias("st", "status")

        # Verify alias exists
        repo = Repository()
        from ugit.utils.config import Config

        config = Config(repo.path)
        alias_cmd = config.get("alias", "st")
        self.assertEqual(alias_cmd, "status")

    def test_list_aliases(self):
        """Test listing aliases."""
        # Create some aliases
        alias("st", "status")
        alias("co", "checkout")

        # List aliases (should not raise)
        alias(list_aliases=True)


class TestInteractiveStaging(TestAdvancedFeaturesBase):
    """Test interactive staging."""

    def test_interactive_staging_setup(self):
        """Test that interactive staging can be set up."""
        # Create files
        with open("file1.txt", "w") as f:
            f.write("content1")
        with open("file2.txt", "w") as f:
            f.write("content2")

        # Interactive staging requires user input, so we'll just test it doesn't crash
        # In a real scenario, we'd mock the input
        try:
            with patch("builtins.input", return_value="q"):
                add_interactive()
        except (EOFError, KeyboardInterrupt):
            # Expected when input is mocked
            pass


class TestGPG(TestAdvancedFeaturesBase):
    """Test GPG functionality."""

    def test_has_gpg_check(self):
        """Test checking if GPG is available."""
        # This should not raise, just return True/False
        result = has_gpg()
        self.assertIsInstance(result, bool)

    def test_gpg_sign_commit_without_gpg(self):
        """Test GPG signing when GPG is not available."""
        # Create commit
        with open("test.txt", "w") as f:
            f.write("test")
        from ugit.commands.add import add
        from ugit.commands.commit import commit

        add("test.txt")
        commit("Initial commit")

        repo = Repository()
        commit_sha = repo.get_head_ref()

        # Try to sign (may fail if GPG not available, which is OK)
        try:
            sign_commit(commit_sha)
        except UgitError:
            # Expected if GPG is not available
            pass


class TestHTTPRemote(TestAdvancedFeaturesBase):
    """Test HTTP remote functionality."""

    def test_http_remote_functions_exist(self):
        """Test that HTTP remote functions exist."""
        from ugit.commands.http_remote import fetch_http, push_http

        self.assertTrue(callable(fetch_http))
        self.assertTrue(callable(push_http))

    def test_http_remote_without_httpx(self):
        """Test HTTP remote when httpx is not available."""
        # Mock httpx as None
        with patch("ugit.commands.http_remote.httpx", None):
            from ugit.commands.http_remote import fetch_http

            with self.assertRaises(UgitError):
                fetch_http("http://example.com/repo")


class TestWebUIEnhancements(TestAdvancedFeaturesBase):
    """Test web UI enhancements."""

    @pytest.mark.skipif(
        os.name == "nt", reason="Web interface tests skipped on Windows"
    )
    def test_web_api_endpoints_exist(self):
        """Test that web API endpoints are defined."""
        try:
            from ugit.web.server import UgitWebServer

            repo = Repository()
            server = UgitWebServer(repo.path)

            # Check that app has routes
            routes = [route.path for route in server.app.routes]
            self.assertIn("/api/blame", routes or [])
            self.assertIn("/api/diff", routes or [])
            self.assertIn("/api/search", routes or [])
        except ImportError:
            pytest.skip("Web dependencies not available")


class TestCrossPlatformCompatibility(TestAdvancedFeaturesBase):
    """Test cross-platform compatibility."""

    def test_path_separators(self):
        """Test that path separators work correctly."""
        # Create nested directories
        nested_path = os.path.join("dir1", "dir2", "file.txt")
        os.makedirs(os.path.dirname(nested_path), exist_ok=True)

        with open(nested_path, "w") as f:
            f.write("content")

        # Add and commit
        from ugit.commands.add import add
        from ugit.commands.commit import commit

        add(nested_path)
        commit("Add nested file")

        # Verify file is tracked (path should be normalized)
        repo = Repository()
        from ugit.core.repository import Index

        index = Index(repo)
        index_data = index.read()
        # Should find the file regardless of platform path separator
        found = any("file.txt" in path for path in index_data.keys())
        self.assertTrue(found)

    def test_file_permissions(self):
        """Test that file permissions work across platforms."""
        # Create file
        test_file = "permissions_test.txt"
        with open(test_file, "w") as f:
            f.write("test")

        # On Unix, we can test permissions
        if os.name != "nt":
            os.chmod(test_file, 0o755)
            stat_info = os.stat(test_file)
            # File should be readable
            self.assertTrue(stat_info.st_mode & 0o444)

    def test_line_endings(self):
        """Test that line endings are handled correctly."""
        # Create file with different line endings
        test_file = "line_endings.txt"
        with open(test_file, "wb") as f:
            f.write(b"line1\nline2\r\nline3\r")

        # Should be readable
        with open(test_file, "r") as f:
            content = f.read()
            self.assertIn("line1", content)


if __name__ == "__main__":
    unittest.main()
