"""Tests for renamer module."""

import pytest
from pathlib import Path
import tempfile
import os

from smartrename.core.renamer import (
    collect_files,
    resolve_conflict,
    preview_rename,
    rename_directory,
)
from smartrename.core.patterns import (
    sequence_pattern,
    lowercase_pattern,
    replace_pattern,
)


def test_collect_files_basic():
    """Test collect_files returns files in directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files
        Path(tmpdir, "file1.txt").write_text("1")
        Path(tmpdir, "file2.txt").write_text("2")
        Path(tmpdir, "subdir").mkdir()
        Path(tmpdir, "subdir", "file3.txt").write_text("3")

        files = collect_files(Path(tmpdir))
        assert len(files) == 2  # Only non-recursive


def test_collect_files_recursive():
    """Test collect_files with recursive option."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "file1.txt").write_text("1")
        Path(tmpdir, "subdir").mkdir()
        Path(tmpdir, "subdir", "file2.txt").write_text("2")

        files = collect_files(Path(tmpdir), recursive=True)
        assert len(files) == 2


def test_collect_files_pattern():
    """Test collect_files with glob pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "image.jpg").write_text("1")
        Path(tmpdir, "doc.txt").write_text("2")
        Path(tmpdir, "photo.jpg").write_text("3")

        files = collect_files(Path(tmpdir), pattern="*.jpg")
        assert len(files) == 2


def test_collect_files_hidden():
    """Test collect_files excludes hidden files by default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "visible.txt").write_text("1")
        Path(tmpdir, ".hidden.txt").write_text("2")

        files = collect_files(Path(tmpdir))
        assert len(files) == 1

        files = collect_files(Path(tmpdir), include_hidden=True)
        assert len(files) == 2


def test_collect_files_empty():
    """Test collect_files returns empty list for empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        files = collect_files(Path(tmpdir))
        assert files == []


def test_resolve_conflict():
    """Test resolve_conflict adds suffix when file exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        existing = Path(tmpdir, "file.txt")
        existing.write_text("original")

        target = Path(tmpdir, "file.txt")  # Same name
        resolved = resolve_conflict(target)

        assert resolved.name == "file_1.txt"
        assert resolved != existing


def test_resolve_conflict_multiple():
    """Test resolve_conflict finds unique name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "file.txt").write_text("1")
        Path(tmpdir, "file_1.txt").write_text("2")

        target = Path(tmpdir, "file.txt")
        resolved = resolve_conflict(target)

        assert resolved.name == "file_2.txt"


def test_preview_rename_sequence():
    """Test preview_rename with sequence pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "a.txt").write_text("1")
        Path(tmpdir, "b.txt").write_text("2")

        files = collect_files(Path(tmpdir))
        func = sequence_pattern(start=1, padding=3)

        ops = preview_rename(files, "sequence", func)

        assert len(ops) == 2
        assert ops[0]["new_name"] == "001_a.txt"
        assert ops[1]["new_name"] == "002_b.txt"


def test_preview_rename_conflict():
    """Test preview_rename handles conflicts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "file.txt").write_text("1")
        Path(tmpdir, "001_file.txt").write_text("2")  # Will conflict

        files = [Path(tmpdir, "file.txt")]
        func = sequence_pattern(start=1, padding=3)

        ops = preview_rename(files, "sequence", func)

        # Should resolve conflict
        assert ops[0]["new_name"] == "001_file_1.txt"


def test_rename_directory_dry_run():
    """Test rename_directory with dry_run doesn't modify files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "UPPER.TXT").write_text("content")

        result = rename_directory(
            Path(tmpdir),
            mode="lowercase",
            dry_run=True,
        )

        assert result["dry_run"]
        # File should not be renamed
        assert Path(tmpdir, "UPPER.TXT").exists()


def test_rename_directory_lowercase():
    """Test rename_directory executes lowercase rename."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "UPPER.TXT").write_text("content")

        result = rename_directory(
            Path(tmpdir),
            mode="lowercase",
            skip_confirm=True,
        )

        assert result["success"]
        # On case-insensitive filesystem (macOS), both paths might return True for exists()
        # So check the actual file listing
        files = [f.name for f in Path(tmpdir).glob("*")]
        assert "upper.txt" in files
        assert "UPPER.TXT" not in files  # Should be renamed


def test_rename_directory_sequence():
    """Test rename_directory executes sequence rename."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "file1.txt").write_text("1")
        Path(tmpdir, "file2.txt").write_text("2")

        result = rename_directory(
            Path(tmpdir),
            mode="sequence",
            start=1,
            padding=3,
            skip_confirm=True,
        )

        assert result["success"]
        assert Path(tmpdir, "001_file1.txt").exists()
        assert Path(tmpdir, "002_file2.txt").exists()


def test_rename_directory_empty():
    """Test rename_directory handles empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = rename_directory(
            Path(tmpdir),
            mode="lowercase",
        )

        assert result["empty"]
        assert result["count"] == 0


def test_rename_directory_creates_history():
    """Test rename_directory saves to history."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "OLD.TXT").write_text("content")

        result = rename_directory(
            Path(tmpdir),
            mode="lowercase",
            skip_confirm=True,
        )

        assert "session_id" in result
        assert result["session_id"]