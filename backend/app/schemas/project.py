"""
============================================================================
 schemas/project.py — Project Pydantic Schemas
============================================================================

PURPOSE:
  Defines the data shapes for project-related API operations
  (create, update, list, detail).

WHY IT EXISTS:
  Same principle as user schemas — we need different shapes for
  different operations:
  - Create: needs title and description
  - Update: title and description are optional (partial update)
  - Response: includes id, timestamps, and note count

HOW IT INTERACTS:
  - Used by api/projects.py to validate requests and format responses
  - Used by services/project_service.py for type hints
============================================================================
"""

from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """
    Schema for creating a new project.

    Example request body:
    {
        "title": "Machine Learning Notes",
        "description": "Notes from my ML course"
    }
    """
    title: str = Field(..., min_length=1, max_length=200, description="Project title")
    description: str = Field(default="", max_length=2000, description="Project description")


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.

    Both fields are optional because the user might only want
    to update the title without changing the description (or vice versa).
    This pattern is called a "partial update."

    Example request body (updating only the title):
    {
        "title": "Updated Title"
    }
    """
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class ProjectResponse(BaseModel):
    """
    Schema for project data in API responses.

    Includes all fields the client needs to display a project.
    from_attributes=True allows Pydantic to read from SQLAlchemy model objects.
    """
    id: int
    title: str
    description: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
