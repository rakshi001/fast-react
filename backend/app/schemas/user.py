"""
============================================================================
 schemas/user.py — User Pydantic Schemas
============================================================================

PURPOSE:
  This file defines the SHAPE of data moving in and out of our API for
  user-related operations (registration, login, profile data).

WHY IT EXISTS:
  Models (models/user.py) define how data is STORED in the database.
  Schemas define how data is SENT and RECEIVED through the API.

  Why separate them? Consider registration:
  - The client sends: { email, password, full_name }
  - We store: { id, email, HASHED_password, full_name, created_at }
  - We return: { id, email, full_name, created_at }  (never the password!)

  Each of these is a different "shape" — that's why we need different schemas.

HOW IT INTERACTS:
  - Used by api/auth.py to validate incoming requests
  - Used by api/auth.py to format outgoing responses
  - Used by services/auth_service.py to type function parameters

CONCEPT — Pydantic BaseModel:
  Pydantic models validate data automatically. If someone sends:
    { "email": 123 }  (number instead of string)
  Pydantic instantly returns a 422 error with a clear message.
  No manual validation code needed!
============================================================================
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# Request Schemas — What the CLIENT sends to US
# ============================================================================

class UserCreate(BaseModel):
    """
    Schema for user registration requests.

    The client sends this when creating a new account.
    Example request body:
    {
        "email": "user@example.com",
        "password": "securepassword",
        "full_name": "John Doe"
    }

    Field() lets us add validation rules:
    - min_length: minimum number of characters
    - max_length: maximum number of characters
    - description: appears in the API docs
    """
    email: EmailStr  # EmailStr validates that it's a proper email format
    password: str = Field(..., min_length=6, max_length=100, description="User password")
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")


class UserLogin(BaseModel):
    """
    Schema for login requests.

    The client sends this when logging in.
    Example request body:
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    """
    email: EmailStr
    password: str


# ============================================================================
# Response Schemas — What WE send back to the CLIENT
# ============================================================================

class UserResponse(BaseModel):
    """
    Schema for user data in API responses.

    Notice: we NEVER include the password/hashed_password here.
    This is a security best practice — the client should never
    see password data, even in hashed form.

    model_config with from_attributes=True tells Pydantic:
    "You can create this schema directly from a SQLAlchemy model object."
    Without this, we'd need to manually convert model → dict → schema.
    """
    id: int
    email: str
    full_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    Schema for the login response — returns the JWT token.

    The client receives this after successful login and stores the
    access_token to use in subsequent requests.

    token_type is always "bearer" — this tells the client to send
    the token as: Authorization: Bearer <token>
    """
    access_token: str
    token_type: str = "bearer"
