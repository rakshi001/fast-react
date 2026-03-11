"""
============================================================================
 api/notes.py — Note API Routes
============================================================================

PURPOSE:
  CRUD endpoints for notes within projects:
  - GET    /projects/{project_id}/notes       — list notes in a project
  - POST   /projects/{project_id}/notes       — create a note in a project
  - GET    /notes/{id}                        — get a single note
  - PUT    /notes/{id}                        — update a note
  - DELETE /notes/{id}                        — delete a note

WHY IT EXISTS:
  Notes are a "nested resource" — they live INSIDE projects. The API
  design reflects this hierarchy:
  - Creating/listing notes → uses /projects/{id}/notes (project context)
  - Viewing/editing/deleting → uses /notes/{id} (direct access by note ID)

  Why the difference? When creating a note, we need to know WHICH project
  it belongs to. When editing, we already know (it's in the note's data).

HOW IT INTERACTS:
  - Mounted by main.py (routes are split across two prefixes)
  - All routes require authentication
  - Delegates to services/note_service.py
============================================================================
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.services import note_service
from app.models.user import User

router = APIRouter(tags=["Notes"])


@router.get("/projects/{project_id}/notes", response_model=list[NoteResponse])
def list_notes(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all notes in a project.

    HTTP: GET /projects/5/notes
    Returns: [ { id, title, content, ... }, ... ]
    """
    return note_service.get_project_notes(db, project_id, current_user.id)


@router.post("/projects/{project_id}/notes", response_model=NoteResponse, status_code=201)
def create_note(
    project_id: int,
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new note in a project.

    HTTP: POST /projects/5/notes
    Body: { title, content }
    Returns: the created note (201 Created)

    Notice: project_id comes from the URL, not the body.
    This prevents mismatches (e.g., body says project 3 but URL says 5).
    """
    return note_service.create_note(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        title=note_data.title,
        content=note_data.content,
    )


@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a single note by ID.

    HTTP: GET /notes/12
    Returns: { id, title, content, project_id, ... }
    """
    return note_service.get_note(db, note_id, current_user.id)


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a note's title and/or content.

    HTTP: PUT /notes/12
    Body: { title?, content? }
    Returns: the updated note
    """
    return note_service.update_note(
        db=db,
        note_id=note_id,
        user_id=current_user.id,
        title=note_data.title,
        content=note_data.content,
    )


@router.delete("/notes/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a note.

    HTTP: DELETE /notes/12
    Returns: nothing (204 No Content)
    """
    note_service.delete_note(db, note_id, current_user.id)
