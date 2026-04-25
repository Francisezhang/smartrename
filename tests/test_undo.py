"""Tests for undo module."""

import pytest
from pathlib import Path
import tempfile
import json
import os

from smartrename.core.undo import (
    load_history,
    save_history,
    create_session,
    add_session,
    list_sessions,
    get_session,
    undo_session,
    clear_history,
    HISTORY_FILE,
)


@pytest.fixture(autouse=True)
def clean_history():
    """Clean history before and after each test."""
    clear_history()
    yield
    clear_history()


def test_load_history_empty():
    """Test load_history returns empty dict when no history."""
    history = load_history()
    assert history == {"sessions": []}


def test_save_and_load_history():
    """Test save_history and load_history work together."""
    history = {"sessions": [{"id": "test123", "operations": []}]}
    save_history(history)

    loaded = load_history()
    assert loaded == history


def test_create_session():
    """Test create_session generates valid session."""
    operations = [{"old_path": "/a/b", "new_path": "/a/c"}]
    session = create_session(operations)

    assert "id" in session
    assert "timestamp" in session
    assert session["operations"] == operations


def test_add_session():
    """Test add_session creates and saves session."""
    operations = [{"old_path": "/test/old.txt", "new_path": "/test/new.txt"}]
    session_id = add_session(operations)

    # Should return session ID
    assert session_id

    # Should be saved
    history = load_history()
    assert len(history["sessions"]) == 1
    assert history["sessions"][0]["id"] == session_id


def test_list_sessions_empty():
    """Test list_sessions returns empty list when no history."""
    sessions = list_sessions()
    assert sessions == []


def test_list_sessions_reversed():
    """Test list_sessions returns sessions in reverse order (most recent first)."""
    add_session([{"old_path": "/a", "new_path": "/b"}])
    add_session([{"old_path": "/c", "new_path": "/d"}])

    sessions = list_sessions()
    assert len(sessions) == 2
    # Most recent should be first
    assert sessions[0]["operations"][0]["old_path"] == "/c"


def test_get_session_found():
    """Test get_session returns session when found."""
    operations = [{"old_path": "/test/old.txt", "new_path": "/test/new.txt"}]
    session_id = add_session(operations)

    session = get_session(session_id)
    assert session is not None
    assert session["id"] == session_id


def test_get_session_not_found():
    """Test get_session returns None when not found."""
    session = get_session("nonexistent")
    assert session is None


def test_undo_session_most_recent():
    """Test undo_session undoes most recent session."""
    # Create temp file
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = Path(tmpdir) / "old.txt"
        new_path = Path(tmpdir) / "new.txt"
        old_path.write_text("content")

        # Rename it
        old_path.rename(new_path)

        # Add session
        add_session([{"old_path": str(old_path), "new_path": str(new_path)}])

        # Undo
        success = undo_session()

        assert success
        assert old_path.exists()
        assert not new_path.exists()


def test_undo_session_specific():
    """Test undo_session undoes specific session by ID."""
    # Create two sessions
    session_id_1 = add_session([{"old_path": "/a/1", "new_path": "/b/1"}])
    session_id_2 = add_session([{"old_path": "/a/2", "new_path": "/b/2"}])

    # Undo first session (should not affect second)
    success = undo_session(session_id_1)

    assert success
    history = load_history()
    assert len(history["sessions"]) == 1
    assert history["sessions"][0]["id"] == session_id_2


def test_undo_session_no_history():
    """Test undo_session returns False when no history."""
    success = undo_session()
    assert not success


def test_clear_history():
    """Test clear_history removes history file."""
    add_session([{"old_path": "/a", "new_path": "/b"}])

    clear_history()

    assert not HISTORY_FILE.exists()
    assert load_history() == {"sessions": []}