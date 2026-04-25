"""SmartRename CLI entry point."""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console

from .core.renamer import collect_files, rename_directory
from .core.undo import list_sessions, undo_session, clear_history, get_session
from .utils.preview import show_file_table, show_preview_table, show_result, show_history_table

app = typer.Typer(
    name="smartrename",
    help="Batch file renaming for macOS — simple, powerful, reversible / 批量文件重命名工具",
    add_completion=False,
)
console = Console()


@app.command("preview")
def preview_cmd(
    directory: Path = typer.Argument(..., help="Directory to preview / 要预览的目录"),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="Glob pattern (e.g. *.jpg) / 文件模式"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Include subdirectories / 包含子目录"),
):
    """
    Preview files in directory / 预览目录中的文件.

    Shows file list with序号、文件名、大小、修改时间.
    """
    files = collect_files(directory, pattern, recursive)
    show_file_table(files, title=f"Files in {directory}")


@app.command("run")
def run_cmd(
    directory: Path = typer.Argument(..., help="Directory to rename / 要重命名的目录"),
    mode: str = typer.Argument(..., help="Rename mode: sequence/date/replace/lowercase/uppercase/clean / 重命名模式"),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="Glob pattern filter / 文件模式筛选"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Include subdirectories / 包含子目录"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Preview only, no execute / 仅预览不执行"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation / 跳过确认"),
    # Mode-specific options
    start: int = typer.Option(1, "--start", help="Start number for sequence mode / 序号起始值"),
    padding: int = typer.Option(3, "--padding", help="Number of digits for sequence mode / 序号位数"),
    find: Optional[str] = typer.Option(None, "--find", help="Pattern to find for replace mode / 查找模式"),
    replace_with: Optional[str] = typer.Option("", "--replace-with", help="Replacement text / 替换文本"),
    use_regex: bool = typer.Option(False, "--regex", help="Use regex in replace mode / 使用正则表达式"),
):
    """
    Rename files in directory / 执行批量重命名.

    Modes 模式:
    - sequence: Add序号前缀 (001_, 002_, ...)
    - date: Add modification date prefix (20240415_)
    - replace: Replace text (regex or simple)
    - lowercase: Convert to lowercase
    - uppercase: Convert to uppercase
    - clean: Clean filename (spaces→underscores, remove brackets)
    """
    # Validate mode
    valid_modes = ["sequence", "date", "replace", "lowercase", "uppercase", "clean"]
    if mode not in valid_modes:
        console.print(f"[red]Error 错误: Invalid mode '{mode}'.[/red]")
        console.print(f"[yellow]Valid modes: {valid_modes}[/yellow]")
        raise typer.Exit(1)

    # Validate replace mode options
    if mode == "replace" and not find:
        console.print("[red]Error 错误: --find is required for replace mode.[/red]")
        raise typer.Exit(1)

    # Build kwargs
    mode_kwargs = {}
    if mode == "sequence":
        mode_kwargs["start"] = start
        mode_kwargs["padding"] = padding
    elif mode == "replace":
        mode_kwargs["find"] = find
        mode_kwargs["replace_with"] = replace_with
        mode_kwargs["use_regex"] = use_regex

    # Preview first
    files = collect_files(directory, pattern, recursive)
    if not files:
        console.print("[yellow]No files found to rename. 没有找到需要重命名的文件[/yellow]")
        return

    # Run rename
    result = rename_directory(
        directory=directory,
        mode=mode,
        pattern=pattern,
        recursive=recursive,
        dry_run=dry_run,
        skip_confirm=yes,
        **mode_kwargs,
    )

    # Show preview
    show_preview_table(result.get("operations", []))

    # Show result
    show_result(result)


@app.command("undo")
def undo_cmd(
    session_id: Optional[str] = typer.Argument(None, help="Session ID to undo / 要撤销的会话ID"),
    list_sessions_flag: bool = typer.Option(False, "--list", "-l", help="List all sessions / 列出所有会话"),
):
    """
    Undo rename operations / 撤销重命名操作.

    Use --list to see all sessions.
    Use session_id to undo a specific session.
    """
    if list_sessions_flag:
        sessions = list_sessions()
        show_history_table(sessions)
        return

    # Get session if ID provided
    if session_id:
        session = get_session(session_id)
        if not session:
            console.print(f"[red]Error 错误: Session '{session_id}' not found.[/red]")
            raise typer.Exit(1)
        console.print(f"[yellow]Undoing session {session_id} ({len(session['operations'])} files)...[/yellow]")
    else:
        sessions = list_sessions()
        if not sessions:
            console.print("[yellow]No history to undo. 没有历史记录[/yellow]")
            return
        console.print(f"[yellow]Undoing last session ({len(sessions[0]['operations'])} files)...[/yellow]")

    # Perform undo
    success = undo_session(session_id)
    if success:
        console.print("[green]Undo successful! 撤销成功[/green]")
    else:
        console.print("[red]Undo failed. 撤销失败[/red]")


@app.command("clean-history")
def clean_history_cmd():
    """
    Clear all history records / 清空所有历史记录.
    """
    clear_history()
    console.print("[green]History cleared. 历史记录已清空[/green]")


if __name__ == "__main__":
    app()