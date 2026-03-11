"""
============================================================================
 services/project_service.py — Project Business Logic
============================================================================

PURPOSE:
  Business rules for project operations. The key rule here is
  AUTHORIZATION — making sure users can only access their own projects.

WHY IT EXISTS:
  The repository handles raw database queries, but doesn't know WHO
  is making the request. The service layer adds ownership checks:
  "Is this user allowed to view/edit/delete this project?"

HOW IT INTERACTS:
  - Called by api/projects.py
  - Calls repositories/project_repository.py
============================================================================
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories import project_repository


def get_user_projects(db: Session, user_id: int):
    """
    Get all projects belonging to the current user.

    Input:  db, user_id — the authenticated user's ID
    Output: list[Project] — the user's projects

    No authorization check needed here — we're already filtering by user_id.
    """
    return project_repository.get_projects_by_user(db, user_id)


def create_project(db: Session, title: str, description: str, user_id: int):
    """
    Create a new project for the current user.

    Input:  db, title, description, user_id
    Output: Project — the newly created project
    """
    return project_repository.create_project(db, title, description, user_id)


def get_project(db: Session, project_id: int, user_id: int):
    """
    Get a single project, ensuring the current user owns it.

    Input:  db, project_id, user_id
    Output: Project — the requested project

    Business rules:
    1. Project must exist → 404 if not found
    2. Project must belong to the current user → 403 if not theirs

    Why separate 404 and 403?
      404 = "this thing doesn't exist"
      403 = "this thing exists but you're not allowed to access it"
      In some apps, you might want to return 404 for both (to hide the
      existence of other users' projects), but for learning, we use
      distinct codes so you can understand what's happening.
    """
    project = project_repository.get_project_by_id(db, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project.",
        )

    return project


def update_project(db: Session, project_id: int, user_id: int, title: str | None, description: str | None):
    """
    Update a project (with ownership verification).

    Input:  db, project_id, user_id, title (optional), description (optional)
    Output: Project — the updated project

    We first call get_project() which handles the 404/403 checks for us.
    This is a pattern called "reuse through composition."
    """
    project = get_project(db, project_id, user_id)
    return project_repository.update_project(db, project, title, description)


def delete_project(db: Session, project_id: int, user_id: int):
    """
    Delete a project (with ownership verification).

    Input:  db, project_id, user_id
    Output: None

    Remember: cascade delete means all notes are also deleted.
    """
    project = get_project(db, project_id, user_id)
    project_repository.delete_project(db, project)
