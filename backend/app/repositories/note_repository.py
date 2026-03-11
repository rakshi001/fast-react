"""
============================================================================
 repositories/note_repository.py — Note Database Operations
============================================================================

PURPOSE:
  All database queries for notes — CRUD operations.

WHY IT EXISTS:
  Same pattern as the project repository. Keeps note-specific
  database logic isolated and reusable.

HOW IT INTERACTS:
  - Called by services/note_service.py
  - Returns Note model objects
============================================================================
"""

from sqlalchemy.orm import Session
from app.models.note import Note


def get_notes_by_project(db: Session, project_id: int) -> list[Note]:
    """
    Get all notes belonging to a specific project.

    Input:  db, project_id
    Output: list[Note] — all notes in the project, newest first

    Why: Used when viewing a project to list all its notes.
    """
    return (
        db.query(Note)
        .filter(Note.project_id == project_id)
        .order_by(Note.updated_at.desc())
        .all()
    )


def get_note_by_id(db: Session, note_id: int) -> Note | None:
    """
    Find a single note by its ID.

    Input:  db, note_id
    Output: Note if found, None otherwise
    """
    return db.query(Note).filter(Note.id == note_id).first()


def create_note(db: Session, title: str, content: str, project_id: int) -> Note:
    """
    Insert a new note into the database.

    Input:  db, title, content, project_id
    Output: Note — the newly created note
    """
    db_note = Note(
        title=title,
        content=content,
        project_id=project_id,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, db_note: Note, title: str | None, content: str | None) -> Note:
    """
    Update an existing note's fields (partial update).

    Input:  db, db_note, title (optional), content (optional)
    Output: Note — the updated note
    """
    if title is not None:
        db_note.title = title
    if content is not None:
        db_note.content = content

    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, db_note: Note) -> None:
    """
    Delete a note from the database.

    Input:  db, db_note — the Note object to delete
    Output: None
    """
    db.delete(db_note)
    db.commit()
