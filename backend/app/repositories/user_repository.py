"""
============================================================================
 repositories/user_repository.py — User Database Operations
============================================================================

PURPOSE:
  This file contains all database queries related to users.
  It's the ONLY place where we write SQL-level logic for users.

WHY IT EXISTS (Repository Pattern):
  In a layered architecture, we separate "how to talk to the database"
  from "what the business rules are." This file handles the HOW:
  - How to find a user by email
  - How to insert a new user row
  - How to fetch a user by ID

  The service layer handles the WHAT (business rules):
  - "A user can't register with an email that's already taken"
  - "A password must be hashed before storing"

  Why separate them?
  1. If we switch databases (e.g., PostgreSQL → MongoDB), we only
     change this file, not the business logic
  2. Database queries are testable in isolation
  3. Clear, single-purpose code is easier to debug

HOW IT INTERACTS:
  - Called by services/auth_service.py
  - Receives a database session from the caller
  - Returns SQLAlchemy model objects (or None)
============================================================================
"""

from sqlalchemy.orm import Session
from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Find a user by their email address.

    Input:  db (Session) — active database session
            email (str) — email to search for
    Output: User object if found, None otherwise

    Why: Used during login (to find the account) and registration
         (to check if the email is already taken).
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Find a user by their primary key (ID).

    Input:  db (Session) — active database session
            user_id (int) — the user's ID
    Output: User object if found, None otherwise

    Why: Used to look up the current user from their JWT token payload.
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, hashed_password: str, full_name: str) -> User:
    """
    Insert a new user into the database.

    Input:  db (Session) — active database session
            email (str) — user's email
            hashed_password (str) — ALREADY hashed password
            full_name (str) — user's display name
    Output: User — the newly created user object (with id set by DB)

    How it works:
    1. Create a User object in Python memory
    2. db.add() marks it for insertion
    3. db.commit() executes the INSERT SQL and saves it
    4. db.refresh() reloads the object with database-generated values
       (like the auto-incremented id and created_at timestamp)

    Why hashed_password and not raw password?
      The repository should NEVER handle password hashing. That's the
      service layer's job. The repository just stores whatever it receives.
    """
    db_user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
