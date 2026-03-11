"""
============================================================================
 models/user.py — User Database Model
============================================================================

PURPOSE:
  This file defines the `users` table in our database. Each row represents
  one registered user of the application.

WHY IT EXISTS:
  In a layered architecture, models define the SHAPE of our data. This
  User model tells SQLAlchemy: "Create a table called 'users' with these
  columns." It's the foundation that everything else builds on.

HOW IT INTERACTS:
  - Inherits from Base (defined in core/database.py)
  - Referenced by Project model (a user HAS MANY projects)
  - Used by repositories/user_repository.py for database queries
  - The columns here map 1:1 to what's stored in PostgreSQL

CONCEPT — ORM Model:
  An ORM model is a Python class where:
  - The class = a database table
  - Each attribute = a column in that table
  - Each instance = a row in that table

  So `User(email="test@test.com")` creates a new row in the users table.
============================================================================
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """
    User model — represents a registered user in the system.

    Table name: "users"

    Columns:
    - id:              Auto-incrementing primary key
    - email:           Unique email address (used for login)
    - hashed_password: Bcrypt hash of the user's password
    - full_name:       User's display name
    - created_at:      When the account was created

    Relationships:
    - projects:  One-to-many relationship with the Project model
                 (a user can have many projects)
    """

    # This tells SQLAlchemy what to name the table in the database
    __tablename__ = "users"

    # ---- Columns ----
    # Column() defines a column. Arguments:
    #   - Type (Integer, String, etc.)
    #   - primary_key: makes this the unique identifier
    #   - unique: no two rows can have the same value
    #   - nullable: whether the column can be empty (NULL)
    #   - index: creates a database index for faster lookups

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ---- Relationships ----
    # relationship() doesn't create a column — it creates a Python-level
    # link between this model and another model.
    #
    # "Project" refers to the Project class (defined in models/project.py)
    # back_populates="owner" means: on the Project model, there's a
    #   corresponding `owner` attribute that links back to this User
    # cascade="all, delete-orphan" means: if we delete a user, also
    #   delete all their projects (and their notes, by extension)
    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        """String representation for debugging (shown in logs/console)."""
        return f"<User(id={self.id}, email={self.email})>"
