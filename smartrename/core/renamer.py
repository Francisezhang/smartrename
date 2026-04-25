"""Core renaming engine with conflict handling and rollback - Cross-platform."""

import os
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Console

from .patterns import get_pattern_func
from .undo import add_session

console = Console()

# Platform detection
CURRENT_PLATFORM = platform.system()
IS_MACOS = CURRENT_PLATFORM == "Darwin"
IS_WINDOWS = CURRENT_PLATFORM == "Windows"
IS_LINUX = CURRENT_PLATFORM == "Linux"


def is_case_insensitive_filesystem(path: Path) -> bool:
    """
    Check if the filesystem is case-insensitive.

    macOS APFS/HFS+ and Windows NTFS are typically case-insensitive.
    Linux ext4 and most Unix filesystems are case-sensitive.
    """
    # macOS and Windows are typically case-insensitive
    if IS_MACOS or IS_WINDOWS:
        return True

    # Linux: test by creating temp files
    if IS_LINUX:
        try:
            test_dir = path if path.is_dir() else path.parent
            test_lower = test_dir / "_test_case_lower_tmp"
            test_upper = test_dir / "_TEST_CASE_LOWER_TMP"

            # Create lower case file
            test_lower.touch()
            # Check if upper case "exists" (case-insensitive)
            result = test_upper.exists()
            # Cleanup
            test_lower.unlink()
            return result
        except Exception:
            # Default to case-sensitive on Linux
            return False

    return False


def collect_files(
    directory: Path,
    pattern: Optional[str] = None,
    recursive: bool = False,
    include_hidden: bool = False,
) -> List[Path]:
    """
    Collect files to rename from directory.

    Args:
        directory: Target directory
        pattern: Glob pattern to filter files (e.g. *.jpg)
        recursive: Whether to recurse into subdirectories
        include_hidden: Whether to include hidden files (. prefix)

    Returns:
        List of file paths
    """
    files = []

    if recursive:
        glob_pattern = "**/*"
    else:
        glob_pattern = "*"

    for item in directory.glob(glob_pattern):
        if not item.is_file():
            continue
        if not include_hidden and item.name.startswith("."):
            continue
        if pattern:
            if not item.match(pattern):
                continue
        files.append(item)

    return sorted(files)


def resolve_conflict(target_path: Path) -> Path:
    """
    Resolve filename conflict by adding _1, _2 suffix.

    Args:
        target_path: Path that already exists

    Returns:
        New path with unique suffix
    """
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent

    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def preview_rename(
    files: List[Path],
    mode: str,
    pattern_func: Callable,
    **kwargs,
) -> List[Dict]:
    """
    Preview rename operations without executing.

    Args:
        files: List of files to rename
        mode: Rename mode
        pattern_func: Function to generate new name
        **kwargs: Additional arguments for pattern

    Returns:
        List of {old_path, new_path, old_name, new_name} dicts
    """
    operations = []

    for idx, filepath in enumerate(files):
        old_name = filepath.name

        # Apply pattern
        if mode == "sequence":
            new_name = pattern_func(idx, filepath)
        elif mode == "date":
            new_name = pattern_func(filepath)
        elif mode == "replace":
            new_name = pattern_func(filepath)
        else:
            new_name = pattern_func(filepath)

        new_path = filepath.parent / new_name

        # Handle conflicts (but not case-only changes on case-insensitive filesystems)
        is_case_only_change = (
            filepath.parent == new_path.parent
            and filepath.name.lower() == new_path.name.lower()
            and filepath.name != new_path.name
        )

        if new_path.exists() and new_path != filepath and not is_case_only_change:
            new_path = resolve_conflict(new_path)
            new_name = new_path.name

        operations.append({
            "old_path": str(filepath),
            "new_path": str(new_path),
            "old_name": old_name,
            "new_name": new_name,
        })

    return operations


def execute_rename(
    operations: List[Dict],
    dry_run: bool = False,
    skip_confirm: bool = False,
) -> Dict:
    """
    Execute rename operations with rollback on error.

    Args:
        operations: List of rename operations
        dry_run: Only preview, don't execute
        skip_confirm: Skip confirmation prompt

    Returns:
        Result dict with success, count, errors
    """
    if dry_run:
        return {"success": True, "count": 0, "errors": [], "dry_run": True}

    if not skip_confirm:
        console.print("\n[yellow]⚠️  Preview above. Execute?[y/N]")
        response = input("> ").strip().lower()
        if response != "y":
            return {"success": False, "count": 0, "errors": [], "cancelled": True}

    executed = []
    errors = []

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3}%"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Renaming...", total=len(operations))

        for op in operations:
            old_path = Path(op["old_path"])
            new_path = Path(op["new_path"])

            try:
                # Handle case-only changes on case-insensitive filesystems
                # (macOS APFS/HFS+, Windows NTFS)
                same_parent = old_path.parent == new_path.parent
                old_name_lower = old_path.name.lower()
                new_name_lower = new_path.name.lower()
                is_case_only_change = (
                    same_parent
                    and old_name_lower == new_name_lower
                    and old_path.name != new_path.name
                )

                if is_case_only_change and is_case_insensitive_filesystem(old_path):
                    # Case-only change on case-insensitive filesystem
                    # Use two-step rename via temp file
                    temp_name = f"_temp_rename_{os.getpid()}_{old_path.name}"
                    temp_path = old_path.parent / temp_name
                    old_path.rename(temp_path)
                    temp_path.rename(new_path)
                else:
                    old_path.rename(new_path)
                executed.append(op)
                progress.advance(task)
            except Exception as e:
                errors.append({"path": str(old_path), "error": str(e)})
                # Rollback already executed operations
                for ex_op in reversed(executed):
                    Path(ex_op["new_path"]).rename(Path(ex_op["old_path"]))
                return {
                    "success": False,
                    "count": len(executed),
                    "errors": errors,
                    "rollback": True,
                }

    # Save to history
    session_id = add_session(executed)

    return {
        "success": True,
        "count": len(executed),
        "errors": errors,
        "session_id": session_id,
    }


def rename_directory(
    directory: Path,
    mode: str,
    pattern: Optional[str] = None,
    recursive: bool = False,
    dry_run: bool = False,
    skip_confirm: bool = False,
    **mode_kwargs,
) -> Dict:
    """
    Main entry point: rename files in directory.

    Args:
        directory: Target directory
        mode: Rename mode (sequence, date, replace, lowercase, uppercase, clean)
        pattern: Glob pattern filter
        recursive: Recursive mode
        dry_run: Preview only
        skip_confirm: No confirmation
        **mode_kwargs: Mode-specific arguments

    Returns:
        Result dict
    """
    # Collect files
    files = collect_files(directory, pattern, recursive)

    if not files:
        return {"success": True, "count": 0, "errors": [], "empty": True}

    # Get pattern function
    pattern_func = get_pattern_func(mode, **mode_kwargs)

    # Preview
    operations = preview_rename(files, mode, pattern_func, **mode_kwargs)

    # Execute
    result = execute_rename(operations, dry_run, skip_confirm)
    result["operations"] = operations

    return result