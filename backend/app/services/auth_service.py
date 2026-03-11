"""
============================================================================
 services/auth_service.py — Authentication Business Logic
============================================================================

PURPOSE:
  This file contains the BUSINESS LOGIC for authentication — the rules
  and decisions that happen between receiving a request and touching
  the database.

WHY A SEPARATE SERVICE LAYER?
  Consider user registration. The process involves:
  1. Check if the email is already taken (database query)
  2. Hash the password (security logic)
  3. Create the user (database insert)
  4. Generate a JWT token (security logic)

  If we put all this in the API route, the route becomes bloated and
  hard to test. Instead:
  - Routes: handle HTTP (parse request, return response)
  - Services: handle business rules (validation, hashing, decisions)
  - Repositories: handle database operations (queries, inserts)

  This separation is called "Separation of Concerns."

HOW IT INTERACTS:
  - Called by api/auth.py (the routes)
  - Calls repositories/user_repository.py (database access)
  - Calls core/security.py (password hashing, JWT tokens)
============================================================================
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories import user_repository
from app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, email: str, password: str, full_name: str):
    """
    Register a new user account.

    Input:  db — database session
            email, password, full_name — from the registration form
    Output: dict — { user, token } on success

    Business rules:
    1. Email must not already be in use → 400 error if taken
    2. Password must be hashed before storing
    3. A JWT token is generated immediately (auto-login after registration)

    Raises: HTTPException(400) if email is already registered
    """
    # Step 1: Check if email is already taken
    existing_user = user_repository.get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    # Step 2: Hash the password (NEVER store plain text!)
    hashed = hash_password(password)

    # Step 3: Create the user in the database
    new_user = user_repository.create_user(db, email, hashed, full_name)

    # Step 4: Generate a JWT token so the user is immediately logged in
    # "sub" is a standard JWT claim meaning "subject" (who is this token for?)
    token = create_access_token({"sub": str(new_user.id)})

    return {"user": new_user, "token": token}


def login_user(db: Session, email: str, password: str):
    """
    Authenticate a user and return a JWT token.

    Input:  db, email, password — from the login form
    Output: dict — { user, token } on success

    Business rules:
    1. User must exist → 401 if not found
    2. Password must match → 401 if wrong
    3. We return the same error for both cases to avoid leaking info
       (attackers shouldn't know if an email exists in our system)

    Raises: HTTPException(401) if credentials are invalid
    """
    # Step 1: Find the user by email
    user = user_repository.get_user_by_email(db, email)

    # Step 2: Verify the password
    # We check both conditions with the same error message intentionally
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 3: Generate and return the JWT token
    token = create_access_token({"sub": str(user.id)})
    return {"user": user, "token": token}
