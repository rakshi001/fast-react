"""
============================================================================
 api/projects.py — Project API Routes
============================================================================

PURPOSE:
  CRUD endpoints for projects:
  - GET    /projects          — list all user's projects
  - POST   /projects          — create a new project
  - GET    /projects/{id}     — get a single project
  - PUT    /projects/{id}     — update a project
  - DELETE /projects/{id}     — delete a project

WHY IT EXISTS:
  These routes form the "Projects" resource in our REST API.
  All routes are PROTECTED — the user must be logged in.

HOW IT INTERACTS:
  - Mounted by main.py with the "/projects" prefix
  - All routes require authentication (get_current_user dependency)
  - Delegates to services/project_service.py

CONCEPT — RESTful Resource Design:
  In REST, a "resource" is a type of thing (projects, notes, users).
  The URL represents the resource, and the HTTP method represents
  the action:

  GET    /projects     → "list all projects"       (Read)
  POST   /projects     → "create a new project"    (Create)
  GET    /projects/5   → "get project with id=5"   (Read one)
  PUT    /projects/5   → "update project 5"        (Update)
  DELETE /projects/5   → "delete project 5"        (Delete)

  This is predictable — any developer seeing these URLs immediately
  understands what they do.
============================================================================
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services import project_service
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all projects for the current user.

    HTTP: GET /projects
    Returns: [ { id, title, description, ... }, ... ]

    Note: `response_model=list[ProjectResponse]` tells FastAPI to:
    1. Convert each SQLAlchemy Project object to a ProjectResponse
    2. Generate the correct schema in API docs
    3. Strip any fields not in ProjectResponse (security!)
    """
    return project_service.get_user_projects(db, current_user.id)


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new project.

    HTTP: POST /projects
    Body: { title, description }
    Returns: the created project
    Status: 201 Created (not 200 OK, because we created a new resource)

    Why status_code=201?
      HTTP convention: 200 = "OK, here's what you asked for"
      201 = "OK, I created something new for you"
      Using correct status codes makes APIs more professional.
    """
    return project_service.create_project(
        db=db,
        title=project_data.title,
        description=project_data.description,
        user_id=current_user.id,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a single project by ID.

    HTTP: GET /projects/5
    Returns: { id, title, description, ... }

    The {project_id} in the URL is a "path parameter."
    FastAPI automatically extracts it and passes it to this function.
    """
    return project_service.get_project(db, project_id, current_user.id)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a project's title and/or description.

    HTTP: PUT /projects/5
    Body: { title?, description? } (both optional)
    Returns: the updated project
    """
    return project_service.update_project(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        title=project_data.title,
        description=project_data.description,
    )


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a project and all its notes.

    HTTP: DELETE /projects/5
    Returns: nothing (204 No Content)

    Why 204? The resource was successfully deleted, so there's
    nothing to return. 204 means "success, but no body."
    """
    project_service.delete_project(db, project_id, current_user.id)
