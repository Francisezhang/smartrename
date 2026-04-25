"""Tests for patterns module."""

import pytest
from pathlib import Path
import tempfile
import os
from datetime import datetime

from smartrename.core.patterns import (
    sequence_pattern,
    date_pattern,
    replace_pattern,
    lowercase_pattern,
    uppercase_pattern,
    clean_pattern,
    get_pattern_func,
)


def test_sequence_pattern_basic():
    """Test sequence pattern with default settings."""
    func = sequence_pattern(start=1, padding=3)
    filepath = Path("test.jpg")

    # Index 0 -> 001_
    assert func(0, filepath) == "001_test.jpg"
    # Index 9 -> 010_
    assert func(9, filepath) == "010_test.jpg"
    # Index 99 -> 100_
    assert func(99, filepath) == "100_test.jpg"


def test_sequence_pattern_custom_start():
    """Test sequence pattern with custom start."""
    func = sequence_pattern(start=10, padding=3)
    filepath = Path("file.txt")

    assert func(0, filepath) == "010_file.txt"
    assert func(5, filepath) == "015_file.txt"


def test_sequence_pattern_custom_padding():
    """Test sequence pattern with custom padding."""
    func = sequence_pattern(start=1, padding=5)
    filepath = Path("doc.pdf")

    assert func(0, filepath) == "00001_doc.pdf"


def test_date_pattern():
    """Test date pattern adds modification date prefix."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)
        # Set modification time to a specific date
        mtime = datetime(2024, 4, 15, 10, 30).timestamp()
        os.utime(tmp_path, (mtime, mtime))

        result = date_pattern(tmp_path)

        # Should have 20240415_ prefix
        assert result.startswith("20240415_")

        # Cleanup
        tmp_path.unlink()


def test_replace_pattern_simple():
    """Test simple string replacement."""
    func = replace_pattern("old", "new")
    filepath = Path("old_file.txt")

    assert func(filepath) == "new_file.txt"


def test_replace_pattern_regex():
    """Test regex replacement."""
    func = replace_pattern(r"\d+", "NUM", use_regex=True)
    filepath = Path("file_123_test.txt")

    assert func(filepath) == "file_NUM_test.txt"


def test_replace_pattern_remove():
    """Test removal by replacing with empty string."""
    func = replace_pattern("copy", "")
    filepath = Path("copy_of_file.txt")

    assert func(filepath) == "_of_file.txt"


def test_lowercase_pattern():
    """Test lowercase conversion."""
    filepath = Path("FILE_NAME.TXT")

    assert lowercase_pattern(filepath) == "file_name.txt"


def test_uppercase_pattern():
    """Test uppercase conversion."""
    filepath = Path("file_name.txt")

    assert uppercase_pattern(filepath) == "FILE_NAME.TXT"


def test_clean_pattern_spaces():
    """Test clean pattern converts spaces to underscores."""
    filepath = Path("my file name.txt")

    assert clean_pattern(filepath) == "my_file_name.txt"


def test_clean_pattern_brackets():
    """Test clean pattern removes brackets."""
    filepath = Path("file [copy] (2).txt")

    assert clean_pattern(filepath) == "file.txt"


def test_clean_pattern_multiple_underscores():
    """Test clean pattern collapses multiple underscores."""
    filepath = Path("file___name.txt")

    assert clean_pattern(filepath) == "file_name.txt"


def test_clean_pattern_leading_trailing():
    """Test clean pattern removes leading/trailing underscores."""
    filepath = Path("_file_name_.txt")

    assert clean_pattern(filepath) == "file_name.txt"


def test_get_pattern_func_valid():
    """Test get_pattern_func returns correct function."""
    func = get_pattern_func("lowercase")
    filepath = Path("TEST.txt")
    assert func(filepath) == "test.txt"


def test_get_pattern_func_invalid():
    """Test get_pattern_func raises for invalid mode."""
    with pytest.raises(ValueError):
        get_pattern_func("invalid_mode")


def test_get_pattern_func_sequence():
    """Test get_pattern_func with sequence kwargs."""
    func = get_pattern_func("sequence", start=5, padding=2)
    filepath = Path("file.txt")
    assert func(0, filepath) == "05_file.txt"


def test_get_pattern_func_replace():
    """Test get_pattern_func with replace kwargs."""
    func = get_pattern_func("replace", find="test", replace_with="demo")
    filepath = Path("test_file.txt")
    assert func(filepath) == "demo_file.txt"