"""
============================================================================
 dependencies/auth.py — Authentication Dependency
============================================================================

PURPOSE:
  Extracts and verifies the current user from the JWT token in the
  request's Authorization header. Used on all "protected" routes.

WHY IT EXISTS:
  Instead of writing token-verification code in every single route,
  we write it ONCE here and use it as a dependency. This is the
  "Don't Repeat Yourself" (DRY) principle in action.

HOW IT INTERACTS:
  - Reads the JWT token from the Authorization header
  - Calls core/security.py to verify the token
  - Calls repositories/user_repository.py to fetch the user from DB
  - Used by all protected routes via Depends(get_current_user)

CONCEPT — OAuth2PasswordBearer:
  This is a FastAPI class that extracts the token from the
  Authorization header automatically. It expects:
    Authorization: Bearer <your-token-here>
  If the header is missing or the format is wrong, it returns 401.

DATA FLOW for a protected request:
  1. Client sends: GET /projects, Authorization: Bearer eyJ...
  2. OAuth2PasswordBearer extracts "eyJ..." from the header
  3. verify_access_token() decodes it → gets user_id
  4. get_user_by_id() looks up the user in the database
  5. The User object is passed to the route handler
============================================================================
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.core.security import verify_access_token
from app.repositories import user_repository


# ============================================================================
# OAuth2 Token Extraction
# ============================================================================
# tokenUrl="auth/login" tells Swagger UI where to send login requests.
# This doesn't affect the actual endpoint — it's just for the docs UI.
# ============================================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Dependency that returns the currently authenticated user.

    Input:  token (str) — extracted from Authorization header by FastAPI
            db (Session) — database session from the get_db dependency
    Output: User — the authenticated user's database record

    Raises: HTTPException(401) if:
    - Token is invalid or expired
    - Token doesn't contain a user ID
    - User ID in the token doesn't exist in the database

    Usage in a route:
        @router.get("/profile")
        def get_profile(current_user: User = Depends(get_current_user)):
            return current_user  # This is the authenticated user
    """
    # Define the error we'll raise for any auth failure
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Step 1: Verify and decode the token
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception

    # Step 2: Extract the user ID from the token's "sub" claim
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    # Step 3: Look up the user in the database
    user = user_repository.get_user_by_id(db, int(user_id_str))
    if user is None:
        raise credentials_exception

    return user
