"""
============================================================================
 services/note_service.py — Note Business Logic
============================================================================

PURPOSE:
  Business rules for note operations. Key rules:
  1. Notes belong to projects, and projects belong to users
  2. A user can only manage notes in their OWN projects

WHY IT EXISTS:
  Notes have a two-level ownership check:
    User → Project → Note
  We must verify both that the project exists AND belongs to the user.

HOW IT INTERACTS:
  - Called by api/notes.py
  - Calls services/project_service.py (for project ownership checks)
  - Calls repositories/note_repository.py (for database operations)
============================================================================
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services import project_service
from app.repositories import note_repository


def get_project_notes(db: Session, project_id: int, user_id: int):
    """
    Get all notes in a project (after verifying ownership).

    Input:  db, project_id, user_id
    Output: list[Note]

    Flow:
    1. Verify the project exists and belongs to the user
    2. Return all notes in that project
    """
    # This will raise 404/403 if the project doesn't exist or isn't theirs
    project_service.get_project(db, project_id, user_id)
    return note_repository.get_notes_by_project(db, project_id)


def create_note(db: Session, project_id: int, user_id: int, title: str, content: str):
    """
    Create a new note in a project (after verifying ownership).

    Input:  db, project_id, user_id, title, content
    Output: Note — the newly created note
    """
    project_service.get_project(db, project_id, user_id)
    return note_repository.create_note(db, title, content, project_id)


def get_note(db: Session, note_id: int, user_id: int):
    """
    Get a single note (after verifying the user owns the parent project).

    Input:  db, note_id, user_id
    Output: Note

    This demonstrates the two-level ownership check:
    1. Find the note → 404 if not found
    2. Check that the note's project belongs to this user → 403 if not
    """
    note = note_repository.get_note_by_id(db, note_id)

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )

    # Verify the user owns the project that contains this note
    project_service.get_project(db, note.project_id, user_id)
    return note


def update_note(db: Session, note_id: int, user_id: int, title: str | None, content: str | None):
    """
    Update a note (with ownership verification).

    Input:  db, note_id, user_id, title (optional), content (optional)
    Output: Note — the updated note
    """
    note = get_note(db, note_id, user_id)
    return note_repository.update_note(db, note, title, content)


def delete_note(db: Session, note_id: int, user_id: int):
    """
    Delete a note (with ownership verification).

    Input:  db, note_id, user_id
    Output: None
    """
    note = get_note(db, note_id, user_id)
    note_repository.delete_note(db, note)
