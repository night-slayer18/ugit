"""Test configuration and utilities for ugit tests."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_repo() -> Generator[Path, None, None]:
    """Create a temporary directory for testing repository operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            yield Path(tmpdir)
        finally:
            os.chdir(old_cwd)


@pytest.fixture
def sample_file(temp_repo: Path) -> Path:
    """Create a sample file for testing."""
    file_path = temp_repo / "test.txt"
    file_path.write_text("Hello, World!")
    return file_path


@pytest.fixture
def initialized_repo(temp_repo: Path) -> Path:
    """Create an initialized ugit repository."""
    from ugit.commands.init import init

    init()
    return temp_repo
