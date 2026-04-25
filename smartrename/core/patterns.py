"""6 renaming patterns: sequence, date, replace, lowercase, uppercase, clean."""

import re
import os
from datetime import datetime
from pathlib import Path
from typing import Callable


def sequence_pattern(start: int = 1, padding: int = 3) -> Callable[[str, Path], str]:
    """
    Add sequence number prefix.

    Args:
        start: Starting number (default 1)
        padding: Number of digits (default 3, e.g. 001, 002)

    Returns:
        Function that takes (index, filepath) and returns new name
    """
    def rename_func(index: int, filepath: Path) -> str:
        num = start + index
        prefix = str(num).zfill(padding)
        return f"{prefix}_{filepath.name}"
    return rename_func


def date_pattern(filepath: Path) -> str:
    """
    Add modification date prefix (YYYYMMDD_).

    Args:
        filepath: Path to file

    Returns:
        New filename with date prefix
    """
    mtime = os.path.getmtime(filepath)
    date_str = datetime.fromtimestamp(mtime).strftime("%Y%m%d")
    return f"{date_str}_{filepath.name}"


def replace_pattern(find: str, replace_with: str, use_regex: bool = False) -> Callable[[Path], str]:
    """
    Replace text in filename using regex or simple string.

    Args:
        find: Pattern to find
        replace_with: Replacement text
        use_regex: Whether to use regex (default False)

    Returns:
        Function that takes filepath and returns new name
    """
    def rename_func(filepath: Path) -> str:
        name = filepath.name
        if use_regex:
            new_name = re.sub(find, replace_with, name)
        else:
            new_name = name.replace(find, replace_with)
        return new_name
    return rename_func


def lowercase_pattern(filepath: Path) -> str:
    """Convert filename to lowercase."""
    return filepath.name.lower()


def uppercase_pattern(filepath: Path) -> str:
    """Convert filename to uppercase."""
    return filepath.name.upper()


def clean_pattern(filepath: Path) -> str:
    """
    Clean filename: spaces→underscores, remove brackets and extra symbols.
    """
    name = filepath.name
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove brackets and their contents
    name = re.sub(r"[\[({][^[\]({)}]*[\])}]", "", name)
    # Remove multiple consecutive underscores
    name = re.sub(r"_+", "_", name)
    # Remove leading/trailing underscores (keep extension)
    stem = Path(name).stem
    ext = Path(name).suffix
    stem = stem.strip("_")
    return f"{stem}{ext}"


def get_pattern_func(mode: str, **kwargs) -> Callable:
    """
    Get the appropriate pattern function based on mode.

    Args:
        mode: One of sequence, date, replace, lowercase, uppercase, clean
        **kwargs: Additional arguments for specific patterns

    Returns:
        Pattern function
    """
    patterns = {
        "sequence": sequence_pattern,
        "date": date_pattern,
        "replace": replace_pattern,
        "lowercase": lowercase_pattern,
        "uppercase": uppercase_pattern,
        "clean": clean_pattern,
    }

    if mode not in patterns:
        raise ValueError(f"Unknown mode: {mode}. Valid modes: {list(patterns.keys())}")

    func = patterns[mode]

    # Handle parameterized patterns
    if mode == "sequence":
        return func(kwargs.get("start", 1), kwargs.get("padding", 3))
    elif mode == "replace":
        return func(kwargs.get("find", ""), kwargs.get("replace_with", ""), kwargs.get("use_regex", False))

    return func