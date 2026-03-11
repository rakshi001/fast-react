"""
============================================================================
 repositories/project_repository.py — Project Database Operations
============================================================================

PURPOSE:
  All database queries for projects — CRUD (Create, Read, Update, Delete).

WHY IT EXISTS:
  Keeps all project-related SQL logic in one place. The service layer
  calls these functions without needing to know SQLAlchemy query syntax.

HOW IT INTERACTS:
  - Called by services/project_service.py
  - Receives a database session and returns model objects
============================================================================
"""

from sqlalchemy.orm import Session
from app.models.project import Project


def get_projects_by_user(db: Session, user_id: int) -> list[Project]:
    """
    Get all projects belonging to a specific user.

    Input:  db (Session) — active database session
            user_id (int) — the owner's user ID
    Output: list[Project] — list of all user's projects

    Why: Used on the dashboard to show all of a user's projects.
    We order by created_at descending so newest projects appear first.
    """
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .all()
    )


def get_project_by_id(db: Session, project_id: int) -> Project | None:
    """
    Find a single project by its ID.

    Input:  db (Session) — active database session
            project_id (int) — the project's primary key
    Output: Project if found, None otherwise

    Why: Used when viewing/editing/deleting a specific project.
    """
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(db: Session, title: str, description: str, user_id: int) -> Project:
    """
    Insert a new project into the database.

    Input:  db, title, description, user_id
    Output: Project — the newly created project (with DB-generated fields)
    """
    db_project = Project(
        title=title,
        description=description,
        user_id=user_id,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, db_project: Project, title: str | None, description: str | None) -> Project:
    """
    Update an existing project's fields.

    Input:  db — database session
            db_project — the existing Project object to update
            title — new title (None means "don't change")
            description — new description (None means "don't change")
    Output: Project — the updated project object

    Why we check for None:
      This supports "partial updates" — the client can send just the
      fields they want to change. If title is None, we keep the current title.
    """
    if title is not None:
        db_project.title = title
    if description is not None:
        db_project.description = description

    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, db_project: Project) -> None:
    """
    Delete a project from the database.

    Input:  db — database session
            db_project — the Project object to delete
    Output: None

    Note: Because of cascade="all, delete-orphan" on the Project model,
    all notes belonging to this project are automatically deleted too.
    """
    db.delete(db_project)
    db.commit()
