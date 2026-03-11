"""
============================================================================
 models/project.py — Project Database Model
============================================================================

PURPOSE:
  This file defines the `projects` table. Each project belongs to a user
  and can contain many notes. Projects are the main organizational unit.

WHY IT EXISTS:
  This model sits in the MIDDLE of our data hierarchy:
    User → Project → Note
  It connects users to their notes through a logical grouping.

HOW IT INTERACTS:
  - Has a FOREIGN KEY to the users table (user_id)
  - Has a ONE-TO-MANY relationship with notes
  - Referenced by repositories/project_repository.py

CONCEPT — Foreign Key:
  A foreign key is a column that references the primary key of another
  table. It creates a LINK between tables. Here, `user_id` in the projects
  table points to `id` in the users table. This means:
  - Every project MUST belong to a user
  - The database enforces this (you can't create a project with a
    non-existent user_id)
============================================================================
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    """
    Project model — represents a container for organizing notes.

    Table name: "projects"

    Columns:
    - id:          Auto-incrementing primary key
    - title:       Project name (e.g., "Machine Learning Notes")
    - description: Optional longer description of the project
    - user_id:     Foreign key linking to the owner (users table)
    - created_at:  When the project was created
    - updated_at:  When the project was last modified

    Relationships:
    - owner: Many-to-one relationship with User (each project has one owner)
    - notes: One-to-many relationship with Note (a project has many notes)
    """

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
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

    # ---- Foreign Key ----
    # ForeignKey("users.id") tells the database: "this column's value
    # MUST match an existing id in the users table."
    # nullable=False means every project MUST have an owner.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ---- Relationships ----
    # `owner` gives us easy Python access to the user who owns this project.
    # Instead of: user = db.query(User).filter(User.id == project.user_id).first()
    # We can do: user = project.owner
    owner = relationship("User", back_populates="projects")

    # `notes` gives us access to all notes in this project.
    # cascade="all, delete-orphan" means: deleting a project also
    # deletes all its notes (notes can't exist without a project).
    notes = relationship(
        "Note",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title})>"
