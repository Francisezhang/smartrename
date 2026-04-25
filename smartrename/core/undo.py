"""History and undo management."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

HISTORY_DIR = Path.home() / ".smartrename"
HISTORY_FILE = HISTORY_DIR / "history.json"


def ensure_history_dir() -> None:
    """Ensure history directory exists."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def load_history() -> Dict:
    """Load history from JSON file."""
    ensure_history_dir()
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sessions": []}


def save_history(history: Dict) -> None:
    """Save history to JSON file."""
    ensure_history_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def create_session(operations: List[Dict]) -> Dict:
    """
    Create a new session with unique ID.

    Args:
        operations: List of {old_path, new_path} dicts

    Returns:
        Session dict with id, timestamp, operations
    """
    return {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "operations": operations,
    }


def add_session(operations: List[Dict]) -> str:
    """
    Add a new session to history.

    Args:
        operations: List of rename operations

    Returns:
        Session ID
    """
    history = load_history()
    session = create_session(operations)
    history["sessions"].append(session)
    save_history(history)
    return session["id"]


def list_sessions() -> List[Dict]:
    """List all sessions (most recent first)."""
    history = load_history()
    return list(reversed(history["sessions"]))


def get_session(session_id: str) -> Optional[Dict]:
    """Get a specific session by ID."""
    history = load_history()
    for session in history["sessions"]:
        if session["id"] == session_id:
            return session
    return None


def undo_session(session_id: Optional[str] = None) -> bool:
    """
    Undo a session (most recent if no ID specified).

    Args:
        session_id: Specific session to undo, or None for most recent

    Returns:
        True if undo succeeded, False otherwise
    """
    history = load_history()

    if not history["sessions"]:
        return False

    if session_id:
        session = get_session(session_id)
        if not session:
            return False
        sessions_to_undo = [session]
        history["sessions"] = [s for s in history["sessions"] if s["id"] != session_id]
    else:
        sessions_to_undo = [history["sessions"][-1]]
        history["sessions"] = history["sessions"][:-1]

    # Perform undo operations
    for session in sessions_to_undo:
        for op in reversed(session["operations"]):
            old_path = Path(op["old_path"])
            new_path = Path(op["new_path"])
            if new_path.exists():
                new_path.rename(old_path)

    save_history(history)
    return True


def clear_history() -> None:
    """Clear all history."""
    ensure_history_dir()
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()