"""Rich preview rendering."""

from pathlib import Path
from typing import List, Dict
from datetime import datetime
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_time(mtime: float) -> str:
    """Format modification time."""
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")


def show_file_table(files: List[Path], title: str = None) -> None:
    """
    Display files in a rich table.

    Args:
        files: List of file paths
        title: Optional table title
    """
    if not files:
        console.print("[yellow]No files found.[/yellow]")
        return

    table = Table(title=title or "File List", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Filename 文件名", style="white")
    table.add_column("Size 大小", style="green", justify="right")
    table.add_column("Modified 修改时间", style="blue")

    for idx, filepath in enumerate(files, 1):
        size = os.path.getsize(filepath)
        mtime = os.path.getmtime(filepath)
        table.add_row(
            str(idx),
            filepath.name,
            format_size(size),
            format_time(mtime),
        )

    console.print(table)
    console.print(f"\n[green]Total: {len(files)} files[/green]")


def show_preview_table(operations: List[Dict]) -> None:
    """
    Display rename preview in a rich table.

    Args:
        operations: List of {old_name, new_name} dicts
    """
    if not operations:
        console.print("[yellow]No operations to preview.[/yellow]")
        return

    table = Table(title="Rename Preview 重命名预览", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Old Name 原名", style="yellow")
    table.add_column("→", style="dim", width=3)
    table.add_column("New Name 新名", style="green")

    for idx, op in enumerate(operations, 1):
        table.add_row(
            str(idx),
            op["old_name"],
            "→",
            op["new_name"],
        )

    console.print(table)
    console.print(f"\n[green]Total: {len(operations)} files to rename[/green]")


def show_result(result: Dict) -> None:
    """
    Display rename result.

    Args:
        result: Result dict from execute_rename
    """
    if result.get("dry_run"):
        console.print(Panel("[yellow]Dry run complete — no files modified[/yellow]", title="Preview Only"))
        return

    if result.get("cancelled"):
        console.print(Panel("[red]Cancelled by user[/red]", title="Aborted"))
        return

    if result.get("empty"):
        console.print(Panel("[yellow]No files to rename[/yellow]", title="Empty Directory"))
        return

    if result.get("rollback"):
        console.print(Panel(
            f"[red]Error occurred, rolled back {result['count']} operations[/red]\n"
            f"Errors: {result['errors']}",
            title="Error with Rollback",
        ))
        return

    if result.get("success"):
        console.print(Panel(
            f"[green]Successfully renamed {result['count']} files[/green]\n"
            f"Session ID: {result.get('session_id', 'N/A')}\n"
            f"[blue]Use smartrename undo to revert[/blue]",
            title="Success 成功",
        ))
    else:
        console.print(Panel(
            f"[red]Rename failed[/red]\n"
            f"Errors: {result.get('errors', [])}",
            title="Error",
        ))


def show_history_table(sessions: List[Dict]) -> None:
    """
    Display history sessions in a rich table.

    Args:
        sessions: List of session dicts
    """
    if not sessions:
        console.print("[yellow]No history found.[/yellow]")
        return

    table = Table(title="History Sessions 历史记录", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Time 时间", style="blue")
    table.add_column("Files 文件数", style="green", justify="right")

    for session in sessions:
        table.add_row(
            session["id"],
            session["timestamp"][:19],  # Remove microseconds
            str(len(session["operations"])),
        )

    console.print(table)