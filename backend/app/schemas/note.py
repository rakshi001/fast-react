"""
============================================================================
 schemas/note.py — Note Pydantic Schemas
============================================================================

PURPOSE:
  Defines the data shapes for note-related API operations.

WHY IT EXISTS:
  Notes are the most frequently created/edited entities, so having
  clear schemas helps both the API and the frontend know exactly
  what data to send and expect.

HOW IT INTERACTS:
  - Used by api/notes.py to validate requests and format responses
  - Used by services/note_service.py for type hints
============================================================================
"""

from datetime import datetime
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """
    Schema for creating a new note within a project.

    Note: project_id is NOT in this schema because it comes from
    the URL path parameter (/projects/{project_id}/notes).
    This avoids duplication and potential mismatches.

    Example request body:
    {
        "title": "Chapter 1 Summary",
        "content": "This chapter covers..."
    }
    """
    title: str = Field(..., min_length=1, max_length=300, description="Note title")
    content: str = Field(default="", description="Note content")


class NoteUpdate(BaseModel):
    """
    Schema for updating an existing note (partial update).

    Example request body (updating only content):
    {
        "content": "Updated content..."
    }
    """
    title: str | None = Field(default=None, min_length=1, max_length=300)
    content: str | None = Field(default=None)


class NoteResponse(BaseModel):
    """
    Schema for note data in API responses.
    """
    id: int
    title: str
    content: str
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
