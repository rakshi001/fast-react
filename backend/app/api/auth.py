"""
============================================================================
 api/auth.py — Authentication API Routes
============================================================================

PURPOSE:
  Defines the HTTP endpoints for user authentication:
  - POST /auth/register — create a new account
  - POST /auth/login — log in and get a JWT token
  - GET  /auth/me — get the current user's profile

WHY IT EXISTS:
  In FastAPI, routes are the "front door" of your API. They:
  1. Receive HTTP requests from the client
  2. Validate the incoming data (using Pydantic schemas)
  3. Call the service layer for business logic
  4. Return formatted responses

  Routes should be THIN — they delegate work to services.
  If you find yourself writing complex logic in a route, it
  probably belongs in a service.

HOW IT INTERACTS:
  - Mounted by main.py with the "/auth" prefix
  - Calls services/auth_service.py for business logic
  - Uses dependencies/auth.py for protected routes (/me)
  - Uses dependencies/database.py for database sessions

CONCEPT — APIRouter:
  APIRouter is like a mini-FastAPI app. It groups related routes
  together with a shared prefix ("/auth") and tags (for API docs).
  This keeps main.py clean — it just mounts the routers.

CONCEPT — REST API Conventions:
  POST = create something new (register, login)
  GET = read something (get current user)
  PUT = update something
  DELETE = remove something
============================================================================
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services import auth_service
from app.models.user import User

# Create a router with "/auth" prefix — all routes here start with /auth
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    HTTP: POST /auth/register
    Body: { email, password, full_name }
    Returns: { access_token, token_type }

    How the data flows:
    1. Client sends JSON body with email, password, full_name
    2. Pydantic (UserCreate) validates the data automatically
       - Is email a valid format? Is password at least 6 chars?
       - If not, FastAPI returns 422 with details
    3. We call auth_service.register_user() for business logic
    4. We return a TokenResponse (the client uses this to stay logged in)
    """
    result = auth_service.register_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )
    return TokenResponse(access_token=result["token"])


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.

    HTTP: POST /auth/login
    Body: { email, password }
    Returns: { access_token, token_type }

    After receiving the token, the client includes it in all requests:
      Authorization: Bearer <token>
    """
    result = auth_service.login_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
    )
    return TokenResponse(access_token=result["token"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the current user's profile.

    HTTP: GET /auth/me
    Headers: Authorization: Bearer <token>
    Returns: { id, email, full_name, created_at }

    This is a PROTECTED route — Depends(get_current_user) verifies
    the JWT token before the route code runs. If the token is invalid,
    FastAPI returns 401 automatically.

    Notice how little code is in this route! The dependency does all
    the heavy lifting. The route just returns the user object.
    """
    return current_user
