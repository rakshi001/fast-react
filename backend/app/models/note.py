"""
============================================================================
 models/note.py — Note Database Model
============================================================================

PURPOSE:
  This file defines the `notes` table. Each note belongs to a project
  and contains the actual content the user writes.

WHY IT EXISTS:
  Notes are the LEAF nodes of our data hierarchy:
    User → Project → Note
  This is the actual content users create and edit.

HOW IT INTERACTS:
  - Has a FOREIGN KEY to the projects table (project_id)
  - Referenced by repositories/note_repository.py
  - The Note model is the most frequently queried model (users
    spend most of their time reading/editing notes)
============================================================================
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Note(Base):
    """
    Note model — represents a piece of content within a project.

    Table name: "notes"

    Columns:
    - id:          Auto-incrementing primary key
    - title:       Note title (e.g., "Chapter 1 Summary")
    - content:     The actual note content (supports long text)
    - project_id:  Foreign key linking to the parent project
    - created_at:  When the note was created
    - updated_at:  When the note was last modified

    Relationships:
    - project: Many-to-one relationship with Project
    """

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, default="")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Foreign key to the projects table
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Relationship back to the parent project
    project = relationship("Project", back_populates="notes")

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title})>"
